"""
api/user.py — 用户/捏人接口

提供用户信息查询和捏人配置的读写。
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user, verify_password, hash_password
from ..models.user import User
from ..schemas.user import (
    AvatarConfig,
    UserResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
)

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    avatar = None
    if user.avatar_config:
        try:
            avatar = AvatarConfig.model_validate_json(user.avatar_config)
        except Exception:
            pass
    return UserResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        avatar_config=avatar,
        created_at=user.created_at,
    )


@router.put("/me", response_model=UserResponse)
async def update_me(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新个人信息（昵称、提醒设置等）"""
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.daily_reminder is not None:
        user.daily_reminder = req.daily_reminder
    if req.reminder_time is not None:
        user.reminder_time = req.reminder_time

    await db.flush()

    avatar = None
    if user.avatar_config:
        try:
            avatar = AvatarConfig.model_validate_json(user.avatar_config)
        except Exception:
            pass

    return UserResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        avatar_config=avatar,
        created_at=user.created_at,
    )


@router.put("/password")
async def change_password(
    req: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(req.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="当前密码错误")

    # 更新密码
    user.hashed_password = hash_password(req.new_password)
    await db.flush()

    return {"message": "密码修改成功"}
