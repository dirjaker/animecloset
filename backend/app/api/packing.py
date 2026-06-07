"""
api/packing.py — 打包清单接口

提供旅行打包清单的增删改查及 AI 自动填充功能。
"""

import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.garment import Garment
from ..models.packing_list import PackingList
from ..schemas.packing import (
    PackingListCreate, PackingListUpdate, PackingListResponse,
)

router = APIRouter(prefix="/packing", tags=["打包清单"])


def _packing_to_response(p: PackingList) -> PackingListResponse:
    items = json.loads(p.items) if p.items else []
    return PackingListResponse(
        id=p.id,
        name=p.name,
        destination=p.destination,
        start_date=str(p.start_date),
        end_date=str(p.end_date),
        items=items,
        notes=p.notes,
        created_at=p.created_at.isoformat(),
    )


@router.get("", response_model=list[PackingListResponse])
async def list_packing_lists(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取用户所有打包清单"""
    result = await db.execute(
        select(PackingList)
        .where(PackingList.user_id == user.id)
        .order_by(PackingList.created_at.desc())
    )
    return [_packing_to_response(p) for p in result.scalars().all()]


@router.post("", response_model=PackingListResponse)
async def create_packing_list(
    data: PackingListCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建打包清单"""
    packing = PackingList(
        user_id=user.id,
        name=data.name,
        destination=data.destination,
        start_date=date.fromisoformat(data.start_date),
        end_date=date.fromisoformat(data.end_date),
    )
    db.add(packing)
    await db.flush()
    return _packing_to_response(packing)


@router.get("/{packing_id}", response_model=PackingListResponse)
async def get_packing_list(
    packing_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取打包清单详情"""
    result = await db.execute(
        select(PackingList).where(
            PackingList.id == packing_id, PackingList.user_id == user.id
        )
    )
    packing = result.scalar_one_or_none()
    if not packing:
        raise HTTPException(status_code=404, detail="清单不存在")
    return _packing_to_response(packing)


@router.put("/{packing_id}", response_model=PackingListResponse)
async def update_packing_list(
    packing_id: str,
    data: PackingListUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新打包清单"""
    result = await db.execute(
        select(PackingList).where(
            PackingList.id == packing_id, PackingList.user_id == user.id
        )
    )
    packing = result.scalar_one_or_none()
    if not packing:
        raise HTTPException(status_code=404, detail="清单不存在")

    if data.name is not None:
        packing.name = data.name
    if data.destination is not None:
        packing.destination = data.destination
    if data.start_date is not None:
        packing.start_date = date.fromisoformat(data.start_date)
    if data.end_date is not None:
        packing.end_date = date.fromisoformat(data.end_date)
    if data.items is not None:
        packing.items = json.dumps(data.items)
    if data.notes is not None:
        packing.notes = data.notes

    await db.flush()
    return _packing_to_response(packing)


@router.delete("/{packing_id}")
async def delete_packing_list(
    packing_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除打包清单"""
    result = await db.execute(
        select(PackingList).where(
            PackingList.id == packing_id, PackingList.user_id == user.id
        )
    )
    packing = result.scalar_one_or_none()
    if not packing:
        raise HTTPException(status_code=404, detail="清单不存在")

    await db.delete(packing)
    return {"message": "已删除"}


@router.post("/{packing_id}/auto-fill", response_model=PackingListResponse)
async def auto_fill_packing(
    packing_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    AI 自动填充打包清单

    根据旅行日期和目的地，从用户衣橱中推荐合适的衣物。
    策略：按天数分配衣物，确保类别覆盖（上衣、下装、鞋等）。
    """
    result = await db.execute(
        select(PackingList).where(
            PackingList.id == packing_id, PackingList.user_id == user.id
        )
    )
    packing = result.scalar_one_or_none()
    if not packing:
        raise HTTPException(status_code=404, detail="清单不存在")

    # 计算旅行天数
    days = (packing.end_date - packing.start_date).days + 1
    if days <= 0:
        raise HTTPException(status_code=400, detail="旅行日期无效")

    # 获取用户所有衣物，按穿着次数排序（优先推荐常穿的）
    garments_result = await db.execute(
        select(Garment)
        .where(Garment.user_id == user.id)
        .order_by(Garment.wear_count.desc())
    )
    all_garments = garments_result.scalars().all()

    # 按类别分组
    by_category: dict[str, list[Garment]] = {}
    for g in all_garments:
        by_category.setdefault(g.category, []).append(g)

    # 基础类别（每天需要的）
    base_categories = ["上衣", "下装", "鞋"]

    # 为每天分配衣物
    items = []
    for day_idx in range(days):
        current_date = packing.start_date + timedelta(days=day_idx)
        day_garment_ids = []

        for cat in base_categories:
            cat_garments = by_category.get(cat, [])
            if cat_garments:
                # 循环使用，避免重复
                pick = cat_garments[day_idx % len(cat_garments)]
                day_garment_ids.append(pick.id)

        items.append({
            "day": day_idx + 1,
            "date": str(current_date),
            "garment_ids": day_garment_ids,
            "occasion": "日常",
        })

    packing.items = json.dumps(items)
    await db.flush()
    return _packing_to_response(packing)
