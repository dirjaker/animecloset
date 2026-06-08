"""
schemas/user.py — 用户/捏人相关请求/响应模型
"""

from datetime import datetime
from pydantic import BaseModel, Field


class AvatarConfig(BaseModel):
    """捏人配置"""
    hair_id: int = 1       # 发型 ID
    skin_id: int = 1       # 肤色 ID
    body_id: int = 1       # 体型 ID
    eye_id: int = 1        # 眼睛类型 ID


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    email: str
    nickname: str
    avatar_config: AvatarConfig | None = None
    created_at: datetime | None = None  # 注册时间

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    """更新个人信息请求"""
    nickname: str | None = Field(None, min_length=2, max_length=50, description="昵称，2-50个字符")
    daily_reminder: bool | None = None
    reminder_time: str | None = None


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1, description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码，至少6位")
