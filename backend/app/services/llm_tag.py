"""
services/llm_tag.py — LLM 智能打标服务

功能：
1. 输入衣物透明图片（base64），调用 DeepSeek Vision 识别属性
2. 输出结构化标签（颜色、材质、风格、季节、场合、温度范围）
3. 降级策略：API 不可用时返回默认标签

调用链路：
图片 base64 → DeepSeek Vision API → 解析 JSON → GarmentTags
"""

import json
import base64
import logging

import httpx

from ..core.config import settings
from ..schemas.garment import GarmentTags

logger = logging.getLogger(__name__)

# 打标提示词
TAG_PROMPT = """你是一个专业的服装鉴定师。请分析这张衣物图片，返回以下JSON格式的标签：

{
  "color": "主颜色（如：黑色、白色、藏青色）",
  "material": "材质（如：棉、涤纶、丝绸、牛仔布、皮革）",
  "style": ["风格1", "风格2"],
  "season": ["适宜季节"],
  "occasion": ["适宜场合"],
  "temp_min": 适宜最低温度(整数,摄氏度),
  "temp_max": 适宜最高温度(整数,摄氏度)
}

字段说明：
- style 可选值：休闲、商务、运动、正式、街头、复古、简约、甜美
- season 可选值：春、夏、秋、冬
- occasion 可选值：工作、日常、聚会、户外、运动、正式场合
- 温度范围根据衣物厚度和材质合理推断

只返回JSON，不要任何额外文字。"""


async def tag_garment(image_bytes: bytes) -> GarmentTags:
    """
    调用多模态LLM为衣物图片打标

    Args:
        image_bytes: 透明背景 PNG 图片的二进制数据

    Returns:
        结构化标签 GarmentTags
    """
    if not settings.DEEPSEEK_API_KEY:
        logger.warning("未配置 DEEPSEEK_API_KEY，使用默认标签")
        return _default_tags()

    try:
        # 图片转 base64
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # 调用 DeepSeek Vision API
        response = await _call_deepseek_vision(img_b64)

        # 解析响应
        tags = _parse_llm_response(response)
        logger.info(f"打标成功: {tags.color} {tags.material} {tags.style}")
        return tags

    except Exception as e:
        logger.error(f"LLM 打标失败: {e}，使用默认标签")
        return _default_tags()


async def _call_deepseek_vision(image_b64: str) -> str:
    """调用 DeepSeek Vision API"""
    url = f"{settings.DEEPSEEK_BASE_URL}/chat/completions"

    payload = {
        "model": "deepseek-chat",  # DeepSeek 支持图片的模型
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TAG_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                        },
                    },
                ],
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _parse_llm_response(response: str) -> GarmentTags:
    """解析 LLM 返回的 JSON 标签"""
    # 清理响应：去掉可能的 markdown 代码块标记
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    data = json.loads(text)
    return GarmentTags(
        color=data.get("color", ""),
        material=data.get("material", ""),
        style=data.get("style", []),
        season=data.get("season", []),
        occasion=data.get("occasion", []),
    )


def _default_tags() -> GarmentTags:
    """默认标签（API 不可用时的降级方案）"""
    return GarmentTags(
        color="未知",
        material="未知",
        style=["休闲"],
        season=["春", "夏", "秋", "冬"],
        occasion=["日常"],
    )
