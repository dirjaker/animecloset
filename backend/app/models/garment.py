"""
models/garment.py — 衣物 ORM 模型

字段：
- id: UUID 主键
- user_id: 所属用户
- original_url: 原始图片路径
- processed_url: 抠图后透明图片路径
- category: 类别（上衣/下装/外套/鞋/配饰）
- tags: JSON 标签（颜色、材质、风格、季节、场合）
- temp_min / temp_max: 适用温度范围
- wear_count: 穿着次数
- last_wear_date: 最后穿着日期
- created_at: 创建时间
"""

import uuid
from datetime import datetime, timezone, date

from sqlalchemy import String, Integer, DateTime, Text, Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class Garment(Base):
    __tablename__ = "garments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # 图片路径
    original_url: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 分类
    category: Mapped[str] = mapped_column(
        String(20), nullable=False, default="上衣"
        # 枚举值: 上衣 / 下装 / 外套 / 鞋 / 配饰
    )

    # 结构化标签（JSON 字符串）
    # 格式: {"color": "黑色", "material": "棉", "style": ["休闲"], "season": ["春","秋"], "occasion": ["日常"]}
    tags: Mapped[str | None] = mapped_column(Text, nullable=True, default="{}")

    # 温度范围（℃）
    temp_min: Mapped[int] = mapped_column(Integer, default=-30)
    temp_max: Mapped[int] = mapped_column(Integer, default=50)

    # 穿着统计
    wear_count: Mapped[int] = mapped_column(Integer, default=0)
    last_wear_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    user = relationship("User", back_populates="garments")

    def __repr__(self) -> str:
        return f"<Garment {self.id[:8]} {self.category}>"
