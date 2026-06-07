"""
models/packing_list.py — 打包清单 ORM 模型

字段：
- id: UUID 主键
- user_id: 所属用户
- name: 旅行名称（如"北京3日游"）
- destination: 目的地
- start_date / end_date: 旅行日期
- items: JSON 行程安排（每天的衣物ID列表）
- notes: 备注
- created_at: 创建时间
"""

import uuid
from datetime import datetime, timezone, date

from sqlalchemy import String, DateTime, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class PackingList(Base):
    __tablename__ = "packing_lists"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # JSON: [{"day": 1, "date": "2026-06-10", "garment_ids": ["id1", "id2"], "occasion": "日常"}]
    items: Mapped[str] = mapped_column(Text, default="[]")

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    user = relationship("User", back_populates="packing_lists")

    def __repr__(self) -> str:
        return f"<PackingList {self.name}>"
