"""
api/user.py — 用户/捏人接口

提供用户信息查询和捏人配置的读写。
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.user import AvatarConfig, UserResponse

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
    )


@router.get("/avatar", response_model=AvatarConfig)
async def get_avatar(user: User = Depends(get_current_user)):
    """获取捏人配置"""
    if not user.avatar_config:
        return AvatarConfig()  # 返回默认配置
    try:
        return AvatarConfig.model_validate_json(user.avatar_config)
    except Exception:
        return AvatarConfig()


@router.put("/avatar", response_model=AvatarConfig)
async def update_avatar(
    config: AvatarConfig,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新捏人配置"""
    user.avatar_config = config.model_dump_json()
    await db.flush()
    return config
