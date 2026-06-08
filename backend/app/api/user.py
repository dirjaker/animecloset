"""
api/user.py — 用户/捏人接口

提供用户信息查询和捏人配置的读写。
"""

import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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

# 头像存储目录
AVATAR_DIR = Path(__file__).parent.parent.parent / "uploads" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


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
        gender=user.gender,
        avatar_url=user.avatar_url,
        avatar_config=avatar,
        created_at=user.created_at,
    )


@router.put("/me", response_model=UserResponse)
async def update_me(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新个人信息"""
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.gender is not None:
        user.gender = req.gender
    if req.avatar_url is not None:
        user.avatar_url = req.avatar_url
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
        gender=user.gender,
        avatar_url=user.avatar_url,
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


@router.post("/avatar/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传头像"""
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    # 验证文件大小 (5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    # 生成唯一文件名
    filename_base = file.filename or "avatar.jpg"
    ext = filename_base.split(".")[-1] if "." in filename_base else "jpg"
    filename = f"{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = AVATAR_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 返回可访问的 URL
    avatar_url = f"/uploads/avatars/{filename}"

    # 更新用户头像 URL
    user.avatar_url = avatar_url
    await db.flush()

    return {"url": avatar_url}
