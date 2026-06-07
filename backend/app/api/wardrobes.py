"""
api/wardrobes.py — 多衣橱管理接口

提供衣橱的增删改查、衣物分配功能。
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.garment import Garment
from ..models.wardrobe import Wardrobe
from ..schemas.wardrobe import (
    WardrobeCreate, WardrobeUpdate, WardrobeResponse, AssignGarmentRequest,
)

router = APIRouter(prefix="/wardrobes", tags=["衣橱管理"])


def _wardrobe_to_response(w: Wardrobe, garment_count: int = 0) -> WardrobeResponse:
    return WardrobeResponse(
        id=w.id,
        name=w.name,
        icon=w.icon,
        sort_order=w.sort_order,
        garment_count=garment_count,
        created_at=w.created_at.isoformat(),
    )


@router.get("", response_model=list[WardrobeResponse])
async def list_wardrobes(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户所有衣橱"""
    result = await db.execute(
        select(Wardrobe)
        .where(Wardrobe.user_id == user.id)
        .order_by(Wardrobe.sort_order, Wardrobe.created_at)
    )
    wardrobes = result.scalars().all()

    resp = []
    for w in wardrobes:
        count_result = await db.execute(
            select(func.count()).select_from(Garment).where(Garment.wardrobe_id == w.id)
        )
        count = count_result.scalar() or 0
        resp.append(_wardrobe_to_response(w, count))
    return resp


@router.post("", response_model=WardrobeResponse)
async def create_wardrobe(
    data: WardrobeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建新衣橱"""
    wardrobe = Wardrobe(
        user_id=user.id,
        name=data.name,
        icon=data.icon,
    )
    db.add(wardrobe)
    await db.flush()
    return _wardrobe_to_response(wardrobe, 0)


@router.put("/{wardrobe_id}", response_model=WardrobeResponse)
async def update_wardrobe(
    wardrobe_id: str,
    data: WardrobeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新衣橱信息"""
    result = await db.execute(
        select(Wardrobe).where(Wardrobe.id == wardrobe_id, Wardrobe.user_id == user.id)
    )
    wardrobe = result.scalar_one_or_none()
    if not wardrobe:
        raise HTTPException(status_code=404, detail="衣橱不存在")

    if data.name is not None:
        wardrobe.name = data.name
    if data.icon is not None:
        wardrobe.icon = data.icon
    if data.sort_order is not None:
        wardrobe.sort_order = data.sort_order

    await db.flush()

    count_result = await db.execute(
        select(func.count()).select_from(Garment).where(Garment.wardrobe_id == wardrobe.id)
    )
    count = count_result.scalar() or 0
    return _wardrobe_to_response(wardrobe, count)


@router.delete("/{wardrobe_id}")
async def delete_wardrobe(
    wardrobe_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除衣橱（衣物移至默认衣橱）"""
    result = await db.execute(
        select(Wardrobe).where(Wardrobe.id == wardrobe_id, Wardrobe.user_id == user.id)
    )
    wardrobe = result.scalar_one_or_none()
    if not wardrobe:
        raise HTTPException(status_code=404, detail="衣橱不存在")

    # 找到或创建默认衣橱
    default_result = await db.execute(
        select(Wardrobe).where(
            Wardrobe.user_id == user.id,
            Wardrobe.name == "默认",
            Wardrobe.id != wardrobe_id,
        )
    )
    default_wardrobe = default_result.scalar_one_or_none()
    if not default_wardrobe:
        default_wardrobe = Wardrobe(user_id=user.id, name="默认", icon="👔")
        db.add(default_wardrobe)
        await db.flush()

    # 把衣物移到默认衣橱
    garments_result = await db.execute(
        select(Garment).where(Garment.wardrobe_id == wardrobe_id)
    )
    for g in garments_result.scalars().all():
        g.wardrobe_id = default_wardrobe.id

    await db.delete(wardrobe)
    return {"message": "已删除，衣物已移至默认衣橱"}


@router.post("/{wardrobe_id}/garments")
async def assign_garment(
    wardrobe_id: str,
    data: AssignGarmentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """将衣物分配到指定衣橱"""
    # 验证衣橱存在
    w_result = await db.execute(
        select(Wardrobe).where(Wardrobe.id == wardrobe_id, Wardrobe.user_id == user.id)
    )
    if not w_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="衣橱不存在")

    # 验证衣物存在
    g_result = await db.execute(
        select(Garment).where(Garment.id == data.garment_id, Garment.user_id == user.id)
    )
    garment = g_result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")

    garment.wardrobe_id = wardrobe_id
    await db.flush()
    return {"message": "已分配", "garment_id": garment.id, "wardrobe_id": wardrobe_id}
