"""
数据库 session 管理

严格模式：所有依赖必须可用，启动时直接报错，绝不允许 mock。
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# 转换 postgresql:// 为 postgresql+asyncpg://
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

# 严格模式：必须创建成功，不允许静默降级
try:
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    logger.info("Database engine initialized: %s", db_url.split("@")[-1])
except Exception as e:
    logger.error("FATAL: Failed to create database engine: %s", e)
    raise RuntimeError(
        f"Database connection failed. Check DATABASE_URL and ensure PostgreSQL "
        f"with pgvector is running. Error: {e}"
    ) from e


async def init_db():
    """初始化数据库（运行 migrations 下的 SQL 文件）"""
    if engine is None:
        raise RuntimeError("Database engine not initialized")

    from pathlib import Path
    migrations_dir = Path(__file__).parent.parent.parent / "migrations"
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        raise FileNotFoundError(f"No .sql files found in {migrations_dir}")

    async with engine.begin() as conn:
        from sqlalchemy import text
        for sql_file in sql_files:
            logger.info("Running migration: %s", sql_file.name)
            sql_content = sql_file.read_text(encoding="utf-8")
            await conn.execute(text(sql_content))

    logger.info("Database initialization complete. Applied %d migrations.", len(sql_files))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：获取数据库 session"""
    if async_session_maker is None:
        raise RuntimeError("Database not configured")
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
