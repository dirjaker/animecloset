"""
services/wanx.py — 通义万相 AI 图像生成服务

将衣物 PNG 拼合成平铺参考图，调用通义万相 API 生成动漫风格穿搭插画。
模型：wanx-style-repaint（人像风格重绘）
"""

import os
import uuid
import httpx
import asyncio
from pathlib import Path
from io import BytesIO
from PIL import Image

from ..core.config import settings

# 通义万相 API 配置
WANX_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
WANX_TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"

# 插画保存目录
ILLUSTRATION_DIR = Path(__file__).parent.parent.parent / "static" / "illustrations"
ILLUSTRATION_DIR.mkdir(parents=True, exist_ok=True)

# 风格 prompt
STYLE_PROMPT = (
    "Q版动漫风格穿搭插画，chibi角色，可爱日系画风，暖色调，柔和光影，"
    "清晰的服装细节，白色背景，全身像，精致可爱"
)

STYLE_NEGATIVE_PROMPT = (
    "真实照片，写实风格，恐怖，暗黑，暴力，裸露，低质量，模糊，变形"
)


async def composite_flat_lay(garment_image_paths: list[str], size: int = 1024) -> BytesIO:
    """
    将多张衣物 PNG 拼合成一张平铺参考图（类似穿搭 flat lay）。

    Args:
        garment_image_paths: 衣物 PNG 文件路径列表
        size: 输出图尺寸（正方形）

    Returns:
        拼合后的图片 BytesIO
    """
    canvas = Image.new("RGBA", (size, size), (255, 255, 255, 255))

    if not garment_image_paths:
        # 没有衣物，返回空白图
        buf = BytesIO()
        canvas.convert("RGB").save(buf, format="JPEG", quality=95)
        buf.seek(0)
        return buf

    n = len(garment_image_paths)

    # 根据衣物数量决定排列方式
    if n == 1:
        positions = [(0.5, 0.5, 0.6)]  # (x_ratio, y_ratio, size_ratio)
    elif n == 2:
        positions = [(0.3, 0.35, 0.4), (0.7, 0.65, 0.4)]
    elif n == 3:
        positions = [(0.5, 0.25, 0.35), (0.3, 0.65, 0.35), (0.7, 0.65, 0.35)]
    elif n == 4:
        positions = [(0.3, 0.25, 0.32), (0.7, 0.25, 0.32),
                     (0.3, 0.65, 0.32), (0.7, 0.65, 0.32)]
    else:
        # 5+ 个衣物：2行排列
        positions = []
        cols = 3
        for i in range(n):
            row = i // cols
            col = i % cols
            x = (col + 0.5) / cols
            y = (row + 0.5) / ((n + cols - 1) // cols)
            s = 0.28
            positions.append((x, y, s))

    for i, img_path in enumerate(garment_image_paths):
        if i >= len(positions):
            break
        try:
            img = Image.open(img_path).convert("RGBA")
        except Exception:
            continue

        x_ratio, y_ratio, size_ratio = positions[i]
        max_dim = int(size * size_ratio)

        # 保持宽高比缩放
        ratio = min(max_dim / img.width, max_dim / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 居中粘贴
        paste_x = int(size * x_ratio - new_w / 2)
        paste_y = int(size * y_ratio - new_h / 2)
        canvas.paste(img_resized, (paste_x, paste_y), img_resized)

    # 转为 RGB（API 需要）
    result = canvas.convert("RGB")
    buf = BytesIO()
    result.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf


async def submit_style_repaint(image_bytes: bytes) -> str:
    """
    提交风格重绘任务到通义万相。

    Args:
        image_bytes: 参考图的字节数据

    Returns:
        task_id
    """
    import base64

    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    payload = {
        "model": "wanx-style-repaint",
        "input": {
            "style": "anime",  # 动漫风格
            "image_url": f"data:image/jpeg;base64,{img_b64}",
        },
        "parameters": {
            "style_index": 0,  # 动漫风格
            "n": 1,
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(WANX_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        result = resp.json()

    if "output" in result and "task_id" in result["output"]:
        return result["output"]["task_id"]

    raise Exception(f"通义万相提交失败: {result}")


async def submit_image_generation(image_bytes: bytes) -> str:
    """
    提交图像生成任务（用文生图 + 参考图方式）。

    Args:
        image_bytes: 参考图的字节数据

    Returns:
        task_id
    """
    import base64

    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    # 使用 wan2.7-image + 参考图
    payload = {
        "model": "wan2.7-image",
        "input": {
            "prompt": STYLE_PROMPT,
            "negative_prompt": STYLE_NEGATIVE_PROMPT,
            "ref_image_url": f"data:image/jpeg;base64,{img_b64}",
        },
        "parameters": {
            "size": "1024*1024",
            "n": 1,
            "ref_strength": 0.7,  # 参考图影响程度
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(WANX_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        result = resp.json()

    if "output" in result and "task_id" in result["output"]:
        return result["output"]["task_id"]

    raise Exception(f"通义万相提交失败: {result}")


async def poll_task(task_id: str, max_wait: int = 120) -> str:
    """
    轮询任务状态，等待完成并返回生成图片的 URL。

    Args:
        task_id: 任务 ID
        max_wait: 最大等待秒数

    Returns:
        生成图片的 URL
    """
    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        for _ in range(max_wait // 2):
            resp = await client.get(f"{WANX_TASK_URL}/{task_id}", headers=headers)
            resp.raise_for_status()
            result = resp.json()

            status = result.get("output", {}).get("task_status", "")

            if status == "SUCCEEDED":
                results = result.get("output", {}).get("results", [])
                if results:
                    return results[0].get("url", "")
                raise Exception("任务完成但没有结果")

            if status == "FAILED":
                msg = result.get("output", {}).get("message", "未知错误")
                raise Exception(f"任务失败: {msg}")

            await asyncio.sleep(2)

    raise Exception("任务超时")


async def download_and_save(image_url: str, outfit_id: str) -> str:
    """
    下载生成的图片并保存到本地。

    Args:
        image_url: 远程图片 URL
        outfit_id: 穿搭记录 ID

    Returns:
        本地相对路径（用于前端访问）
    """
    filename = f"{outfit_id}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = ILLUSTRATION_DIR / filename

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()
        filepath.write_bytes(resp.content)

    # 返回相对路径
    return f"/static/illustrations/{filename}"


async def generate_outfit_illustration(
    garment_image_paths: list[str],
    outfit_id: str,
) -> str:
    """
    完整流程：拼合衣物图 → 调通义万相 → 保存插画。

    Args:
        garment_image_paths: 衣物 PNG 路径列表
        outfit_id: 穿搭记录 ID

    Returns:
        插画的本地相对路径
    """
    if not settings.DASHSCOPE_API_KEY:
        raise Exception("未配置 DASHSCOPE_API_KEY，请在 .env 文件中设置")

    # 1. 拼合平铺参考图
    flat_lay_buf = await composite_flat_lay(garment_image_paths)
    image_bytes = flat_lay_buf.read()

    # 2. 提交风格重绘任务
    task_id = await submit_image_generation(image_bytes)

    # 3. 轮询等待结果
    image_url = await poll_task(task_id)

    # 4. 下载保存
    local_path = await download_and_save(image_url, outfit_id)

    return local_path
