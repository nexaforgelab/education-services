"""
pytest fixtures and configuration

严格模式：测试需要真实的 PostgreSQL + pgvector 和 ANTHROPIC_API_KEY。
如果测试环境没有这些依赖，将自动跳过集成测试。
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient

# 把 backend 加入 path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _check_db_available() -> bool:
    """检查 PostgreSQL 是否可用"""
    try:
        import asyncpg
        url = os.environ.get("DATABASE_URL", "postgresql://education:education@localhost:5432/education_services")
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        # 移除 SQLAlchemy 的 +asyncpg 后缀以便 asyncpg 直连测试
        test_url = url.replace("postgresql+asyncpg://", "postgresql://")
        async def _check():
            try:
                conn = await asyncpg.connect(test_url, timeout=2)
                await conn.close()
                return True
            except Exception:
                return False
        return asyncio.run(_check())
    except Exception:
        return False


def _check_llm_available() -> bool:
    """检查 ANTHROPIC_API_KEY 是否设置"""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


DB_AVAILABLE = _check_db_available()
LLM_AVAILABLE = _check_llm_available()

# 跳过装饰器
requires_db = pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="需要真实 PostgreSQL+pgvector。设置 DATABASE_URL 或启动 docker-compose up postgres"
)
requires_llm = pytest.mark.skipif(
    not LLM_AVAILABLE,
    reason="需要 ANTHROPIC_API_KEY 才能运行 LLM 集成测试"
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """设置测试环境"""
    os.environ.setdefault("ENV", "test")
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://education:education@localhost:5432/education_services_test"

    # 如果 DB 可用，确保 schema 已建
    if DB_AVAILABLE:
        try:
            from app.db.session import init_db
            asyncio.run(init_db())
        except Exception as e:
            print(f"Warning: init_db failed: {e}")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI 测试客户端"""
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_token() -> str:
    """生成测试用 JWT token"""
    from app.core.security import create_access_token
    return create_access_token("test_user_001", "teacher", "测试教师")


@pytest.fixture
def parent_token() -> str:
    """家长 token"""
    from app.core.security import create_access_token
    return create_access_token("parent_001", "parent", "测试家长")


@pytest.fixture
def admin_token() -> str:
    """管理员 token"""
    from app.core.security import create_access_token
    return create_access_token("admin_001", "admin", "测试管理员")


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """带认证的 headers"""
    return {"Authorization": f"Bearer {auth_token}"}
