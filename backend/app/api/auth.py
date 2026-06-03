"""
api/auth.py — 认证接口

提供注册和登录两个端点。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token
from ..models.user import User
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册

    1. 检查邮箱是否已注册
    2. 创建用户（密码 bcrypt 哈希）
    3. 返回 JWT 令牌
    """
    # 检查邮箱唯一性
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已注册")

    # 创建用户
    user = User(
        email=req.email,
        nickname=req.nickname,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.flush()  # 获取生成的 ID

    # 生成令牌
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        nickname=user.nickname,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录

    1. 验证邮箱和密码
    2. 返回 JWT 令牌
    """
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        nickname=user.nickname,
    )
