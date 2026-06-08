#!/usr/bin/env python3
"""
init_db.py — 初始化 PostgreSQL + pgvector 数据库

执行 backend/migrations/ 下的所有 SQL 文件，创建表、索引、扩展。

用法:
  python scripts/init_db.py
  python scripts/init_db.py --drop-first  # 危险：先删除所有表
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
except ImportError:
    print("Error: pip install sqlalchemy asyncpg --break-system-packages", file=sys.stderr)
    sys.exit(1)


# 加载 .env
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def get_db_url() -> str:
    """获取并转换数据库 URL"""
    load_env()
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("Error: DATABASE_URL not set. Please set in .env or environment.", file=sys.stderr)
        sys.exit(1)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return db_url


async def check_extension(engine, ext_name: str):
    """检查扩展是否可用"""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name, installed_version, default_version FROM pg_available_extensions WHERE name = :n"),
            {"n": ext_name}
        )
        row = result.fetchone()
        if not row:
            raise RuntimeError(f"扩展 {ext_name} 不可用。请使用 pgvector 镜像：pgvector/pgvector:pg16")
        return row


async def init_db(drop_first: bool = False):
    """初始化数据库"""
    db_url = get_db_url()
    print(f"🔌 连接到数据库: {db_url.split('@')[-1]}")

    engine = create_async_engine(db_url, echo=False)

    try:
        # 1. 测试连接
        async with engine.connect() as conn:
            version = await conn.execute(text("SELECT version()"))
            print(f"   PostgreSQL: {version.scalar()}")

        # 2. 检查扩展
        print("📦 检查扩展...")
        await check_extension(engine, "vector")
        await check_extension(engine, "uuid-ossp")
        print("   ✅ pgvector 和 uuid-ossp 可用")

        # 3. 删除所有表（可选）
        if drop_first:
            print("⚠️  正在删除所有表...")
            async with engine.begin() as conn:
                await conn.execute(text("""
                DROP TABLE IF EXISTS citations CASCADE;
                DROP TABLE IF EXISTS agent_outputs CASCADE;
                DROP TABLE IF EXISTS learning_events CASCADE;
                DROP TABLE IF EXISTS homework_records CASCADE;
                DROP TABLE IF EXISTS student_profiles CASCADE;
                DROP TABLE IF EXISTS knowledge_points CASCADE;
                DROP TABLE IF EXISTS textbook_blocks CASCADE;
                DROP TABLE IF EXISTS textbooks CASCADE;
                DROP FUNCTION IF EXISTS update_updated_at CASCADE;
                """))
            print("   ✅ 已删除所有表")

        # 4. 运行所有 migrations
        migrations_dir = Path(__file__).parent.parent / "backend" / "migrations"
        if not migrations_dir.exists():
            raise FileNotFoundError(f"Migrations 目录不存在: {migrations_dir}")

        sql_files = sorted(migrations_dir.glob("*.sql"))
        if not sql_files:
            raise FileNotFoundError(f"Migrations 目录为空: {migrations_dir}")

        async with engine.begin() as conn:
            for sql_file in sql_files:
                print(f"   📝 运行: {sql_file.name}")
                sql = sql_file.read_text(encoding="utf-8")
                await conn.execute(text(sql))

        # 5. 验证表已创建
        async with engine.connect() as conn:
            result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' ORDER BY table_name
            """))
            tables = [r[0] for r in result.fetchall()]
            print(f"\n✅ 已创建 {len(tables)} 张表:")
            for t in tables:
                print(f"   - {t}")

    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="初始化数据库")
    parser.add_argument("--drop-first", action="store_true", help="先删除所有表（危险）")
    args = parser.parse_args()

    asyncio.run(init_db(drop_first=args.drop_first))


if __name__ == "__main__":
    main()
