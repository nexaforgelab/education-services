#!/bin/bash
# Hermes 一键安装脚本
#
# 用法（在 Hermes 服务器上）：
#   curl -fsSL https://raw.githubusercontent.com/education-services/education-services/main/dist/hermes-install.sh | bash
#
# 或本地：
#   ./dist/hermes-install.sh

set -euo pipefail

BUNDLE_NAME="education-services"
INSTALL_DIR="${HERMES_HOME:-$HOME/.hermes}/bundles/$BUNDLE_NAME"
REPO_URL="https://github.com/education-services/education-services/archive/refs/tags/v0.1.0.tar.gz"

echo "🦉 Installing $BUNDLE_NAME for Hermes Agent..."
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

# 3. Python 依赖
echo "🐍 安装 Python 依赖..."
cd "$INSTALL_DIR"
pip install -r requirements-dev.txt --break-system-packages --quiet

# 4. 后端基础设施
if ! command -v docker >/dev/null 2>&1; then
  echo "⚠️  Docker 未安装"
else
  echo "🐘 启动 PostgreSQL + MinIO..."
  docker compose up -d postgres minio
  sleep 8
fi

# 5. 初始化 DB
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  请编辑 $INSTALL_DIR/.env 填入 ANTHROPIC_API_KEY"
fi

python scripts/init_db.py || { echo "❌ DB 初始化失败"; exit 1; }
python scripts/seed_data.py

# 6. 启动 MCP servers
echo "🔌 启动 MCP servers..."
nohup python scripts/serve_mcp_servers.py > /tmp/edu_mcp.log 2>&1 &
echo "   MCP 日志: /tmp/edu_mcp.log"

# 7. 注册到 Hermes
echo "🛠️  注册到 Hermes..."
hermes skills add "$INSTALL_DIR" --bundle "$INSTALL_DIR/dist/hermes/education-services.hermes/bundle.json"

# 8. 部署所有 cookbook
echo "🤖 部署 Agent cookbooks..."
for cookbook in managed-agent-cookbooks/*/; do
  if [ -f "$cookbook/agent.yaml" ]; then
    name=$(basename "$cookbook")
    echo "   - $name"
    python scripts/orchestrate.py deploy --cookbook "$cookbook"
  fi
done

echo ""
echo "✅ 安装完成！"
echo ""
echo "📋 后续步骤："
echo "   1. 编辑 $INSTALL_DIR/.env 填入 ANTHROPIC_API_KEY"
echo "   2. 重启 MCP servers: kill -9 \$(pgrep -f serve_mcp_servers) && nohup python $INSTALL_DIR/scripts/serve_mcp_servers.py &"
echo "   3. 测试: hermes chat '教我七年级有理数加减法'"
echo "   4. 命令行: hermes invoke textbook-teaching-agent /lesson-plan '有理数加减法 45 中等'"
echo ""
echo "📖 详细文档：$INSTALL_DIR/docs/OpenClaw-Hermes-使用文档.docx"
