"""
api/wardrobes.py — 多衣橱管理接口

提供衣橱的增删改查、衣物分配功能。
"""

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


async def _find_default_wardrobe(db: AsyncSession, user_id: str) -> Wardrobe | None:
    """查找用户的默认衣橱（sort_order 最小的那个）"""
    result = await db.execute(
        select(Wardrobe)
        .where(Wardrobe.user_id == user_id)
        .order_by(Wardrobe.sort_order, Wardrobe.created_at)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _ensure_default_wardrobe(db: AsyncSession, user_id: str) -> Wardrobe:
    """确保用户有默认衣橱，没有则创建"""
    default = await _find_default_wardrobe(db, user_id)
    if not default:
        default = Wardrobe(user_id=user_id, name="默认", icon="👔", sort_order=0)
        db.add(default)
        await db.flush()
    return default


@router.get("", response_model=list[WardrobeResponse])
async def list_wardrobes(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户所有衣橱"""
    # 使用子查询一次性获取所有衣橱的衣物数量，避免 N+1 查询
    count_subq = (
        select(Garment.wardrobe_id, func.count().label("cnt"))
        .where(Garment.wardrobe_id.isnot(None))
        .group_by(Garment.wardrobe_id)
        .subquery()
    )
    result = await db.execute(
        select(Wardrobe, func.coalesce(count_subq.c.cnt, 0).label("garment_count"))
        .outerjoin(count_subq, Wardrobe.id == count_subq.c.wardrobe_id)
        .where(Wardrobe.user_id == user.id)
        .order_by(Wardrobe.sort_order, Wardrobe.created_at)
    )
    rows = result.all()
    return [_wardrobe_to_response(w, count) for w, count in rows]


@router.post("", response_model=WardrobeResponse)
async def create_wardrobe(
    data: WardrobeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建新衣橱"""
    # 自动计算 sort_order：取当前最大值 + 1
    max_result = await db.execute(
        select(func.max(Wardrobe.sort_order))
        .where(Wardrobe.user_id == user.id)
    )
    next_sort = (max_result.scalar() or -1) + 1

    wardrobe = Wardrobe(
        user_id=user.id,
        name=data.name,
        icon=data.icon,
        sort_order=next_sort,
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

    # 检查是否是最后一个衣橱
    count_result = await db.execute(
        select(func.count()).select_from(Wardrobe).where(Wardrobe.user_id == user.id)
    )
    if (count_result.scalar() or 0) <= 1:
        raise HTTPException(status_code=400, detail="不能删除最后一个衣橱")

    # 找到目标衣橱（sort_order 最小的非当前衣橱）
    target_result = await db.execute(
        select(Wardrobe)
        .where(Wardrobe.user_id == user.id, Wardrobe.id != wardrobe_id)
        .order_by(Wardrobe.sort_order, Wardrobe.created_at)
        .limit(1)
    )
    target_wardrobe = target_result.scalar_one_or_none()
    if not target_wardrobe:
        raise HTTPException(status_code=500, detail="无法找到目标衣橱")

    # 把衣物移到默认衣橱
    garments_result = await db.execute(
        select(Garment).where(Garment.wardrobe_id == wardrobe_id)
    )
    moved_count = 0
    for g in garments_result.scalars().all():
        g.wardrobe_id = target_wardrobe.id
        moved_count += 1

    await db.flush()  # 先 flush 确保衣物移动完成
    await db.delete(wardrobe)
    return {
        "message": "已删除",
        "moved_garments": moved_count,
        "target_wardrobe_id": target_wardrobe.id,
    }


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


@router.delete("/{wardrobe_id}/garments/{garment_id}")
async def remove_garment(
    wardrobe_id: str,
    garment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """将衣物从指定衣橱移除（移至默认衣橱）"""
    # 验证衣橱存在
    w_result = await db.execute(
        select(Wardrobe).where(Wardrobe.id == wardrobe_id, Wardrobe.user_id == user.id)
    )
    if not w_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="衣橱不存在")

    # 验证衣物存在且属于该衣橱
    g_result = await db.execute(
        select(Garment).where(
            Garment.id == garment_id,
            Garment.user_id == user.id,
            Garment.wardrobe_id == wardrobe_id,
        )
    )
    garment = g_result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在或不属于该衣橱")

    # 移至默认衣橱
    default = await _ensure_default_wardrobe(db, user.id)
    garment.wardrobe_id = default.id
    await db.flush()
    return {"message": "已移除", "garment_id": garment.id, "target_wardrobe_id": default.id}
