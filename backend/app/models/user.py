"""
models/user.py — 用户 ORM 模型

字段：
- id: UUID 主键
- email: 邮箱（唯一）
- nickname: 昵称
- hashed_password: bcrypt 密码哈希
- avatar_config: 捏人配置 JSON
- daily_reminder: 是否开启每日穿搭提醒
- reminder_time: 提醒时间（HH:MM）
- created_at: 创建时间
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 捏人配置：JSON 字符串，存储发型/肤色/体型 ID
    avatar_config: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    # 每日穿搭提醒
    daily_reminder: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_time: Mapped[str | None] = mapped_column(String(5), nullable=True, default="08:00")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    garments = relationship("Garment", back_populates="user", lazy="selectin")
    outfits = relationship("Outfit", back_populates="user", lazy="selectin")
    wardrobes = relationship("Wardrobe", back_populates="user", lazy="selectin")
    packing_lists = relationship("PackingList", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
