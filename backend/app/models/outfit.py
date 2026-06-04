"""
models/outfit.py — 穿搭记录 ORM 模型

字段：
- id: UUID 主键
- user_id: 所属用户
- date: 穿搭日期（同一天同一用户唯一）
- garment_ids: 衣物ID列表（JSON数组，按上衣/下装/外套/鞋/配饰顺序）
- weather: 天气状况
- temperature: 温度
- reason: 推荐理由
- created_at: 创建时间
"""

import uuid
from datetime import datetime, timezone, date

from sqlalchemy import String, Integer, DateTime, Text, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # 穿搭日期
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # 衣物ID列表（JSON数组）
    # 格式: ["garment_id_1", "garment_id_2", ...]
    # 顺序: [上衣, 下装, 外套, 鞋, 配饰]，缺失项为 null
    garment_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    # 当日天气
    weather: Mapped[str | None] = mapped_column(String(50), nullable=True)
    temperature: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 推荐理由
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI 生成的穿搭插画路径
    illustration_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    user = relationship("User", back_populates="outfits")

    # 同一天同一用户只能有一条穿搭记录
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date_outfit"),
    )

    def __repr__(self) -> str:
        return f"<Outfit {self.date} {self.user_id[:8]}>"
