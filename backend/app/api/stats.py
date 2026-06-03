"""
api/stats.py — 衣橱统计接口

提供衣物统计数据：各类别数量、穿着排行、冷宫衣物等。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.garment import Garment
from ..schemas.garment import GarmentResponse, GarmentTags

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/wardrobe")
async def wardrobe_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    衣橱概览统计

    返回：各类别衣物数量、总数、穿着总次数
    """
    # 各类别计数
    result = await db.execute(
        select(Garment.category, func.count())
        .where(Garment.user_id == user.id)
        .group_by(Garment.category)
    )
    category_counts = {row[0]: row[1] for row in result.all()}

    # 总数
    total = sum(category_counts.values())

    # 穿着总次数
    wear_result = await db.execute(
        select(func.sum(Garment.wear_count))
        .where(Garment.user_id == user.id)
    )
    total_wears = wear_result.scalar() or 0

    return {
        "total": total,
        "by_category": category_counts,
        "total_wears": total_wears,
    }


@router.get("/cold-palace")
async def cold_palace(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    冷宫衣物：超过 N 天未穿着的衣物

    Args:
        days: 天数阈值，默认30天
    """
    cutoff = date.today() - timedelta(days=days)

    result = await db.execute(
        select(Garment)
        .where(
            Garment.user_id == user.id,
            # 从未穿过 或 最后穿着日期超过阈值
            (Garment.last_wear_date == None) | (Garment.last_wear_date < cutoff)
        )
        .order_by(Garment.last_wear_date.asc())
    )
    garments = result.scalars().all()

    from ..schemas.garment import GarmentTags

    items = []
    for g in garments:
        tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
        items.append({
            "id": g.id,
            "category": g.category,
            "tags": tags.model_dump(),
            "wear_count": g.wear_count,
            "last_wear_date": str(g.last_wear_date) if g.last_wear_date else "从未穿过",
            "days_since": (date.today() - g.last_wear_date).days if g.last_wear_date else None,
        })

    return {
        "threshold_days": days,
        "count": len(items),
        "items": items,
    }


@router.get("/wear-ranking")
async def wear_ranking(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """穿着次数排行榜"""
    result = await db.execute(
        select(Garment)
        .where(Garment.user_id == user.id)
        .order_by(Garment.wear_count.desc())
        .limit(limit)
    )
    garments = result.scalars().all()

    items = []
    for g in garments:
        tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
        items.append({
            "id": g.id,
            "category": g.category,
            "tags": tags.model_dump(),
            "wear_count": g.wear_count,
            "last_wear_date": str(g.last_wear_date) if g.last_wear_date else None,
        })

    return {"items": items}
