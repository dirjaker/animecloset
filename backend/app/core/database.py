"""
database.py — 数据库连接与会话管理

使用 SQLAlchemy 2.0 async 模式 + aiosqlite 驱动。
提供 AsyncSession 工厂和依赖注入函数。
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL 日志
)

# 异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """ORM 基类，所有模型继承此类"""
    pass


async def get_db():
    """
    FastAPI 依赖注入：获取数据库会话

    自动提交：请求成功时 commit，异常时 rollback。
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """创建所有表（开发用，生产环境应使用 alembic 迁移）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
