#!/usr/bin/env bash
# Education Services — 一键开发启动脚本
# 用法: bash scripts/dev.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "========================================="
echo " Education Services — 开发环境启动"
echo "========================================="
echo ""

# 1. 检查 .env
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env，从模板创建..."
    cp .env.example .env
    echo "   ✅ 已创建 .env，请填入 ANTHROPIC_API_KEY"
    echo ""
fi

# 2. 检查 Python 依赖
echo "📦 检查 Python 依赖..."
pip install fastapi uvicorn pydantic pydantic-settings structlog pyjwt \
    sqlalchemy asyncpg pyyaml httpx \
    --break-system-packages -q 2>/dev/null || true

# 3. 运行结构校验
echo ""
echo "🔍 运行项目结构校验..."
python scripts/validate.py || true

# 4. 启动后端
echo ""
echo "🚀 启动 FastAPI 后端 (http://localhost:8000)..."
echo "   API 文档: http://localhost:8000/docs"
echo "   按 Ctrl+C 停止"
echo ""

cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
