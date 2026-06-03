"""
api/outfits.py — 穿搭接口

提供穿搭的保存、查询和日历展示功能。
"""

import json
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.outfit import Outfit
from ..models.garment import Garment
from ..schemas.outfit import (
    OutfitSave, OutfitResponse, GarmentBrief,
    CalendarResponse, CalendarDay,
)
from ..schemas.garment import GarmentTags
from ..services.weather import get_weather

router = APIRouter(prefix="/outfits", tags=["穿搭"])


def _build_outfit_response(outfit: Outfit, garments_map: dict) -> OutfitResponse:
    """构建穿搭响应（含衣物详情）"""
    garment_ids = json.loads(outfit.garment_ids) if outfit.garment_ids else []

    garment_briefs = []
    for gid in garment_ids:
        if gid and gid in garments_map:
            g = garments_map[gid]
            tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
            garment_briefs.append(GarmentBrief(
                id=g.id,
                category=g.category,
                processed_url=g.processed_url,
                tags=tags.model_dump(),
            ))

    return OutfitResponse(
        id=outfit.id,
        date=str(outfit.date),
        garment_ids=garment_ids,
        garments=garment_briefs,
        weather=outfit.weather,
        temperature=outfit.temperature,
        reason=outfit.reason,
    )


@router.post("", response_model=OutfitResponse)
async def save_outfit(
    req: OutfitSave,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    保存穿搭

    若该日期已有穿搭记录，则覆盖。
    保存时自动更新衣物的穿着次数和最后穿着日期。
    """
    target_date = date.fromisoformat(req.date)

    # 检查是否已有该日穿搭
    existing = await db.execute(
        select(Outfit).where(
            and_(Outfit.user_id == user.id, Outfit.date == target_date)
        )
    )
    existing_outfit = existing.scalar_one_or_none()

    if existing_outfit:
        # 覆盖：先还原旧穿搭的穿着次数
        old_ids = json.loads(existing_outfit.garment_ids)
        for gid in old_ids:
            if gid:
                result = await db.execute(
                    select(Garment).where(Garment.id == gid, Garment.user_id == user.id)
                )
                g = result.scalar_one_or_none()
                if g and g.wear_count > 0:
                    g.wear_count -= 1

    # 获取天气
    weather_info = await get_weather()

    # 验证衣物ID有效性
    garment_ids = [gid for gid in req.garment_ids if gid]
    if garment_ids:
        result = await db.execute(
            select(Garment.id).where(
                and_(Garment.id.in_(garment_ids), Garment.user_id == user.id)
            )
        )
        valid_ids = {row[0] for row in result.all()}
        invalid = [gid for gid in garment_ids if gid not in valid_ids]
        if invalid:
            raise HTTPException(status_code=400, detail=f"衣物不存在: {invalid}")

    # 更新穿着次数和最后穿着日期
    today = date.today()
    for gid in garment_ids:
        result = await db.execute(
            select(Garment).where(Garment.id == gid, Garment.user_id == user.id)
        )
        g = result.scalar_one_or_none()
        if g:
            if g.last_wear_date != today:
                g.wear_count += 1
                g.last_wear_date = today

    # 保存或更新穿搭
    if existing_outfit:
        existing_outfit.garment_ids = json.dumps(req.garment_ids)
        existing_outfit.weather = weather_info["weather"]
        existing_outfit.temperature = weather_info["temperature"]
        outfit = existing_outfit
    else:
        outfit = Outfit(
            user_id=user.id,
            date=target_date,
            garment_ids=json.dumps(req.garment_ids),
            weather=weather_info["weather"],
            temperature=weather_info["temperature"],
        )
        db.add(outfit)

    await db.flush()

    # 构建响应
    result = await db.execute(
        select(Garment).where(Garment.user_id == user.id)
    )
    garments_map = {g.id: g for g in result.scalars().all()}

    return _build_outfit_response(outfit, garments_map)


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    month: str = "",  # YYYY-MM 格式
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    获取日历数据

    Args:
        month: 月份 YYYY-MM，默认当前月

    Returns:
        该月每天的穿搭记录
    """
    if not month:
        today = date.today()
        year, mon = today.year, today.month
    else:
        parts = month.split("-")
        year, mon = int(parts[0]), int(parts[1])

    # 查询该月所有穿搭
    result = await db.execute(
        select(Outfit).where(
            and_(
                Outfit.user_id == user.id,
                extract("year", Outfit.date) == year,
                extract("month", Outfit.date) == mon,
            )
        )
    )
    outfits = result.scalars().all()

    # 获取相关衣物
    all_garment_ids = set()
    for o in outfits:
        ids = json.loads(o.garment_ids)
        all_garment_ids.update(gid for gid in ids if gid)

    garments_map = {}
    if all_garment_ids:
        g_result = await db.execute(
            select(Garment).where(Garment.id.in_(all_garment_ids))
        )
        garments_map = {g.id: g for g in g_result.scalars().all()}

    # 构建日历数据
    outfits_by_date = {str(o.date): o for o in outfits}

    # 生成该月所有日期
    import calendar
    days_in_month = calendar.monthrange(year, mon)[1]
    days = []
    for day in range(1, days_in_month + 1):
        d = date(year, mon, day)
        d_str = str(d)
        if d_str in outfits_by_date:
            outfit_resp = _build_outfit_response(outfits_by_date[d_str], garments_map)
            days.append(CalendarDay(date=d_str, outfit=outfit_resp))
        else:
            days.append(CalendarDay(date=d_str, outfit=None))

    return CalendarResponse(year=year, month=mon, days=days)
