"""
api/garments.py — 衣物接口

Phase 1: 基础骨架，后续 Phase 2 补充上传和抠图逻辑。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.garment import Garment
from ..schemas.garment import (
    GarmentResponse, GarmentUpdate, GarmentListResponse, GarmentTags,
)
import json

router = APIRouter(prefix="/garments", tags=["衣橱"])


def _garment_to_response(g: Garment) -> GarmentResponse:
    """ORM 对象 → 响应模型"""
    tags = GarmentTags.model_validate_json(g.tags) if g.tags else GarmentTags()
    return GarmentResponse(
        id=g.id,
        original_url=g.original_url,
        processed_url=g.processed_url,
        category=g.category,
        tags=tags,
        temp_min=g.temp_min,
        temp_max=g.temp_max,
        wear_count=g.wear_count,
        last_wear_date=str(g.last_wear_date) if g.last_wear_date else None,
        created_at=g.created_at.isoformat(),
    )


@router.get("", response_model=GarmentListResponse)
async def list_garments(
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    获取衣橱列表（分页 + 类别筛选）
    """
    query = select(Garment).where(Garment.user_id == user.id)
    count_query = select(func.count()).select_from(Garment).where(Garment.user_id == user.id)

    if category:
        query = query.where(Garment.category == category)
        count_query = count_query.where(Garment.category == category)

    # 总数
    total = (await db.execute(count_query)).scalar()

    # 分页
    query = query.order_by(Garment.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    garments = result.scalars().all()

    return GarmentListResponse(
        items=[_garment_to_response(g) for g in garments],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{garment_id}", response_model=GarmentResponse)
async def get_garment(
    garment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取单件衣物详情"""
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.user_id == user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")
    return _garment_to_response(garment)


@router.put("/{garment_id}", response_model=GarmentResponse)
async def update_garment(
    garment_id: str,
    update: GarmentUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新衣物信息（标签、类别、温度范围）"""
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.user_id == user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")

    if update.category is not None:
        garment.category = update.category
    if update.tags is not None:
        garment.tags = update.tags.model_dump_json()
    if update.temp_min is not None:
        garment.temp_min = update.temp_min
    if update.temp_max is not None:
        garment.temp_max = update.temp_max

    await db.flush()
    return _garment_to_response(garment)


@router.delete("/{garment_id}")
async def delete_garment(
    garment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除衣物"""
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.user_id == user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=404, detail="衣物不存在")

    await db.delete(garment)
    return {"message": "已删除"}
