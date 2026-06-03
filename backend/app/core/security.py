"""
security.py — JWT 认证与密码哈希

职责：
1. 密码哈希（bcrypt）
2. JWT 令牌生成与验证
3. 当前用户依赖注入
"""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer Token 提取器
security_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """明文密码 → bcrypt 哈希"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    """
    生成 JWT 令牌

    Args:
        user_id: 用户 UUID
        expires_delta: 过期时间增量

    Returns:
        JWT 字符串
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": user_id,  # subject = 用户ID
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> str:
    """
    解析 JWT 令牌

    Returns:
        用户 UUID

    Raises:
        HTTPException 401: 令牌无效或过期
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证令牌")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    FastAPI 依赖注入：获取当前登录用户

    从 Authorization: Bearer <token> 中解析用户ID，查询数据库返回用户对象。
    """
    from ..models.user import User  # 避免循环导入

    user_id = decode_access_token(credentials.credentials)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
