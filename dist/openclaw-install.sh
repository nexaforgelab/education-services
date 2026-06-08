#!/bin/bash
# OpenClaw 一键安装脚本
#
# 用法：
#   curl -fsSL https://raw.githubusercontent.com/education-services/education-services/main/dist/openclaw-install.sh | bash
#
# 或本地：
#   ./dist/openclaw-install.sh

set -euo pipefail

BUNDLE_NAME="education-services"
INSTALL_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/bundles/$BUNDLE_NAME"
REPO_URL="https://github.com/education-services/education-services/archive/refs/tags/v0.1.0.tar.gz"

echo "🚀 Installing $BUNDLE_NAME for OpenClaw..."
echo "   Install dir: $INSTALL_DIR"
echo ""

# 1. 准备目录
mkdir -p "$INSTALL_DIR"

# 2. 下载 / 复制源码
if [ -d "../../education-services" ]; then
  echo "📦 复制本地源码..."
  cp -r ../../education-services/* "$INSTALL_DIR/"
else
  echo "📦 下载源码包..."
  curl -fsSL "$REPO_URL" | tar -xz -C "$INSTALL_DIR" --strip-components=1
fi

# 3. 检查 / 安装 Python 依赖
echo "🐍 安装 Python 依赖..."
pip install -r "$INSTALL_DIR/requirements-dev.txt" --break-system-packages --quiet

# 4. 检查 / 启动 PostgreSQL
if ! command -v docker >/dev/null 2>&1; then
  echo "⚠️  Docker 未安装，请先安装 Docker 后手动启动 PostgreSQL+pgvector"
else
  echo "🐘 启动 PostgreSQL+pgvector 容器..."
  cd "$INSTALL_DIR" && docker compose up -d postgres minio
  sleep 8
fi

# 5. 初始化数据库
echo "📚 初始化数据库..."
cd "$INSTALL_DIR"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  请编辑 $INSTALL_DIR/.env 填入 ANTHROPIC_API_KEY"
fi

python scripts/init_db.py || { echo "❌ 数据库初始化失败，请检查 PostgreSQL 是否运行"; exit 1; }
python scripts/seed_data.py

# 6. 注册到 OpenClaw
echo "🔌 注册到 OpenClaw..."
openclaw skills add "$INSTALL_DIR" --manifest "$INSTALL_DIR/dist/clawhub/education-services.claw/manifest.json"
openclaw mcp add "$INSTALL_DIR/plugins/vertical-plugins/education-core/.mcp.json"

# 7. 验证
echo ""
echo "✅ 安装完成！"
echo ""
echo "📋 后续步骤："
echo "   1. 编辑 $INSTALL_DIR/.env 填入 ANTHROPIC_API_KEY"
echo "   2. 启动 OpenClaw: openclaw start"
echo "   3. 在 OpenClaw 中尝试: /lesson-plan 有理数加减法 45 中等"
echo ""
echo "📖 详细文档：$INSTALL_DIR/docs/OpenClaw-Hermes-使用文档.docx"
echo "💬 反馈：https://github.com/education-services/education-services/issues"
