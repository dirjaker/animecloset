"""
api/share.py — 社交分享接口

提供穿搭分享图片生成功能：将穿搭中的衣物图片拼接成拼图，叠加日期和天气文字。
"""

import os
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image, ImageDraw, ImageFont

from ..core.config import settings
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.garment import Garment
from ..models.outfit import Outfit

router = APIRouter(prefix="/share", tags=["分享"])

# 分享图片输出目录
SHARE_DIR = Path("static/share")
SHARE_DIR.mkdir(parents=True, exist_ok=True)

# 图片尺寸配置
THUMB_SIZE = (200, 200)
PADDING = 20
TEXT_AREA_HEIGHT = 80
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (60, 60, 60)


@router.post("/outfit/{outfit_id}")
async def share_outfit(
    outfit_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    生成穿搭分享图片

    将穿搭中的衣物图片拼接成一行拼图，底部叠加日期和天气文字。
    返回可访问的图片 URL。
    """
    # 获取穿搭记录
    result = await db.execute(
        select(Outfit).where(Outfit.id == outfit_id, Outfit.user_id == user.id)
    )
    outfit = result.scalar_one_or_none()
    if not outfit:
        raise HTTPException(status_code=404, detail="穿搭不存在")

    garment_ids = json.loads(outfit.garment_ids) if outfit.garment_ids else []
    garment_ids = [gid for gid in garment_ids if gid]  # 去除 null

    if not garment_ids:
        raise HTTPException(status_code=400, detail="穿搭中没有衣物")

    # 获取衣物信息
    garments_result = await db.execute(
        select(Garment).where(Garment.id.in_(garment_ids), Garment.user_id == user.id)
    )
    garments = {g.id: g for g in garments_result.scalars().all()}

    # 加载衣物图片
    images: list[Image.Image] = []
    for gid in garment_ids:
        g = garments.get(gid)
        if not g:
            continue
        img_path = g.processed_url or g.original_url
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGBA")
                img.thumbnail(THUMB_SIZE, Image.LANCZOS)
                images.append(img)
            except Exception:
                continue

    if not images:
        raise HTTPException(status_code=400, detail="无法加载衣物图片")

    # 计算拼图尺寸
    n = len(images)
    total_width = PADDING * (n + 1) + THUMB_SIZE[0] * n
    total_height = PADDING * 2 + THUMB_SIZE[1] + TEXT_AREA_HEIGHT

    # 创建画布
    canvas = Image.new("RGB", (total_width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # 粘贴衣物图片
    x_offset = PADDING
    for img in images:
        # 居中粘贴（考虑缩放后实际尺寸）
        paste_y = PADDING + (THUMB_SIZE[1] - img.height) // 2
        paste_x = x_offset + (THUMB_SIZE[0] - img.width) // 2
        if img.mode == "RGBA":
            canvas.paste(img, (paste_x, paste_y), img)
        else:
            canvas.paste(img, (paste_x, paste_y))
        x_offset += THUMB_SIZE[0] + PADDING

    # 添加文字
    text_y = PADDING + THUMB_SIZE[1] + 15
    info_parts = [str(outfit.date)]
    if outfit.weather:
        info_parts.append(outfit.weather)
    if outfit.temperature is not None:
        info_parts.append(f"{outfit.temperature}℃")
    info_text = " | ".join(info_parts)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except (OSError, IOError):
        font = ImageFont.load_default()

    # 居中绘制文字
    bbox = draw.textbbox((0, 0), info_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (total_width - text_width) // 2
    draw.text((text_x, text_y), info_text, fill=TEXT_COLOR, font=font)

    # 保存图片
    filename = f"outfit_{uuid.uuid4().hex[:12]}.png"
    output_path = SHARE_DIR / filename
    canvas.save(str(output_path), "PNG")

    # 返回可访问的 URL
    share_url = f"/static/share/{filename}"
    return {"url": share_url, "filename": filename}
