"""
api/stats.py — 衣橱统计接口

提供衣物统计数据：各类别数量、穿着排行、冷宫衣物等。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
import json
from collections import defaultdict

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


@router.get("/monthly")
async def monthly_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """最近12个月每月穿着统计"""
    from ..models.outfit import Outfit

    today = date.today()
    months = []
    for i in range(11, -1, -1):
        # 计算每个月的第一天
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        first_day = date(year, month, 1)
        # 下个月第一天
        if month == 12:
            next_first = date(year + 1, 1, 1)
        else:
            next_first = date(year, month + 1, 1)

        result = await db.execute(
            select(func.count()).select_from(Outfit).where(
                Outfit.user_id == user.id,
                Outfit.date >= first_day,
                Outfit.date < next_first,
            )
        )
        count = result.scalar() or 0
        months.append({
            "month": f"{year}-{month:02d}",
            "count": count,
        })

    return {"months": months}


@router.get("/category-distribution")
async def category_distribution(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """衣物类别分布统计"""
    result = await db.execute(
        select(Garment.category, func.count())
        .where(Garment.user_id == user.id)
        .group_by(Garment.category)
    )
    distribution = [{"category": row[0], "count": row[1]} for row in result.all()]
    return {"distribution": distribution}


@router.get("/cost-per-wear")
async def cost_per_wear(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """每次穿着成本（仅含购买价格的衣物）"""
    result = await db.execute(
        select(Garment)
        .where(
            Garment.user_id == user.id,
            Garment.purchase_price.isnot(None),
            Garment.purchase_price > 0,
        )
        .order_by(Garment.purchase_price / func.greatest(Garment.wear_count, 1))
    )
    garments = result.scalars().all()

    items = []
    for g in garments:
        cpw = round(g.purchase_price / max(g.wear_count, 1), 2)
        tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
        items.append({
            "id": g.id,
            "category": g.category,
            "tags": tags.model_dump(),
            "purchase_price": g.purchase_price,
            "wear_count": g.wear_count,
            "cost_per_wear": cpw,
        })

    return {"items": items}


@router.get("/season-distribution")
async def season_distribution(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """按季节标签统计衣物分布"""
    result = await db.execute(
        select(Garment).where(Garment.user_id == user.id)
    )
    garments = result.scalars().all()

    season_counts: dict[str, int] = defaultdict(int)
    for g in garments:
        tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
        if tags.season:
            for s in tags.season:
                season_counts[s] += 1
        else:
            season_counts["未分类"] += 1

    return {"distribution": [{"season": k, "count": v} for k, v in season_counts.items()]}


@router.get("/wear-trend")
async def wear_trend(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """最近30天每日穿着次数"""
    from ..models.outfit import Outfit

    today = date.today()
    start = today - timedelta(days=29)

    result = await db.execute(
        select(Outfit.date, func.count())
        .where(Outfit.user_id == user.id, Outfit.date >= start, Outfit.date <= today)
        .group_by(Outfit.date)
        .order_by(Outfit.date)
    )
    existing = {str(row[0]): row[1] for row in result.all()}

    days = []
    for i in range(30):
        d = start + timedelta(days=i)
        days.append({
            "date": str(d),
            "count": existing.get(str(d), 0),
        })

    return {"days": days}
