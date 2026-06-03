"""
schemas/auth.py — 认证相关请求/响应模型
"""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """注册请求"""
    email: str         # 邮箱
    password: str      # 密码（明文，传输时用HTTPS）
    nickname: str      # 昵称


class LoginRequest(BaseModel):
    """登录请求"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """登录成功返回"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    nickname: str
