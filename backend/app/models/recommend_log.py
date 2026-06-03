"""
models/recommend_log.py — 推荐日志 ORM 模型（调试用）

记录每次推荐请求的完整上下文，用于调试和成本分析。
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class RecommendLog(Base):
    __tablename__ = "recommend_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # 请求上下文（JSON）
    request_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 发送给大模型的完整提示词
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 大模型返回的原始响应
    llm_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 用户最终选择的衣物ID列表（JSON）
    selected_ids: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<RecommendLog {self.id[:8]}>"
