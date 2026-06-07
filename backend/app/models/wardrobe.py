"""
models/wardrobe.py — 多衣橱管理 ORM 模型

字段：
- id: UUID 主键
- user_id: 所属用户
- name: 衣橱名称（如"日常"、"正式"、"运动"）
- icon: 图标标识
- sort_order: 排序顺序
- created_at: 创建时间
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class Wardrobe(Base):
    __tablename__ = "wardrobes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="👔")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    user = relationship("User", back_populates="wardrobes")
    garments = relationship("Garment", back_populates="wardrobe", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Wardrobe {self.name}>"
