# Education Services — Makefile
.PHONY: help install dev test validate eval lint docker-up docker-down clean

help:  ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装所有依赖
	pip install -r requirements-dev.txt --break-system-packages

dev:  ## 启动开发服务
	bash scripts/dev.sh

test:  ## 运行后端单元测试
	cd backend && python -m pytest tests/ -v --tb=short

validate:  ## 运行项目结构校验
	python scripts/validate.py

eval:  ## 运行 eval 测试用例
	pip install pyyaml --break-system-packages -q && python scripts/eval_agent.py --all

lint:  ## 代码质量检查
	ruff check backend/ scripts/
	ruff format --check backend/ scripts/

format:  ## 自动格式化
	ruff format backend/ scripts/

docker-up:  ## 启动 Docker 服务
	docker-compose up -d

docker-down:  ## 停止 Docker 服务
	docker-compose down

clean:  ## 清理临时文件
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

sync-skills:  ## 同步 agent-skills 映射
	python scripts/sync-agent-skills.py
