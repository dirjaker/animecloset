"""
schemas/user.py — 用户/捏人相关请求/响应模型
"""

from pydantic import BaseModel


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

    model_config = {"from_attributes": True}
