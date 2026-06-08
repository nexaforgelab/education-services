# 📚 Education Services

> **Textbook-driven AI agent pack for teachers and parents** — built on the [Anthropic financial-services architecture](https://github.com/anthropics/financial-services), adapted for the education domain.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/education-services/education-services/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Validate](https://img.shields.io/badge/validate-passing-brightgreen.svg)](scripts/validate.py)
[![Evals](https://img.shields.io/badge/evals-12%2F12-brightgreen.svg)](scripts/eval_agent.py)
[![Skills](https://img.shields.io/badge/skills-56-blueviolet.svg)](plugins/vertical-plugins)
[![Agents](https://img.shields.io/badge/agents-5-orange.svg)](plugins/agent-plugins)
[![MCP](https://img.shields.io/badge/mcp_servers-5-yellowgreen.svg)](plugins/vertical-plugins/education-core/.mcp.json)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/security-policy-blue.svg)](SECURITY.md)

[🇨🇳 中文文档](#中文) | [🇺🇸 English](#english)

---

## English

### What is Education Services?

Education Services is an open-source **AI agent pack** for K-12 education. It is **not** a "student answer bot" — it is a textbook-driven tutoring agent designed to help:

- **Teachers** prepare lessons, grade homework, and diagnose student errors
- **Parents** understand what their child is learning and tutor effectively
- **Students** (with teacher/parent supervision) get scaffolded, Socratic-style help

The system is grounded in a single principle: **every output must be traceable to a specific textbook page**. No hallucination, no fabrication.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📖 **Textbook-grounded** | All agent outputs reference specific chapter, page, or question number |
| 🛡️ **Strict non-mock mode** | Refuses to start without real PostgreSQL, real Claude API, real PDF parser |
| 🔒 **7 guardrails** | Citation required · no cheating · privacy · injection defense · professional boundary · ... |
| 🧩 **5 named agents** | Textbook Teaching · Lesson Planner · Homework Diagnosis · Unit Review · Parent Coach |
| 🛠 **56 Skills** | Reusable Markdown knowledge bases for math, Chinese, English, science, teacher & parent workflows |
| 🔌 **5 MCP servers** | textbook_store · vector_index · student_profile · homework_store · question_bank |
| 🪶 **7 slash commands** | `/lesson-plan` · `/diagnose-homework` · `/explain-to-parent` · ... |
| 🤖 **7 subagents** | Read-only by default · only `feedback-writer` has write permission |
| 🚀 **3 deployment modes** | Cowork plugin · Managed Agent (Hermes) · FastAPI backend |
| 🌍 **Bilingual** | English + Chinese content throughout |

### 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│  Cowork Plugin │ Hermes Agent │ FastAPI Backend / WebSocket  │
└─────────────┬─────────────┬──────────────────┬───────────────┘
              │             │                  │
        ┌─────▼─────┐ ┌─────▼──────┐ ┌────────▼────────┐
        │  Agent    │ │  Agent     │ │   Agent         │
        │  Plugins  │ │  Cookbooks │ │   Backends      │
        │  (5)      │ │  (5)       │ │   (FastAPI)     │
        └─────┬─────┘ └─────┬──────┘ └────────┬────────┘
              │             │                  │
        ┌─────▼─────────────▼──────────────────▼────────┐
        │     Skills (56 SKILL.md knowledge bases)      │
        └─────────────────────┬─────────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────────┐
        │  MCP Servers (5)                              │
        │  textbook_store / vector_index / student_...  │
        └─────────────────────┬─────────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────────┐
        │  PostgreSQL + pgvector │ MinIO/S3             │
        └───────────────────────────────────────────────┘
```

### 🚀 Quick Start

#### Option 1: As a Cowork Plugin (Claude Code / Cursor)

```bash
# Clone the repo
git clone https://github.com/education-services/education-services.git
cd education-services

# Install dependencies
pip install -r requirements-dev.txt --break-system-packages

# Validate project structure
python scripts/validate.py        # 6/6 ✅
python scripts/eval_agent.py --all  # 12/12 ✅
```

#### Option 2: As a Backend Service

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY=sk-ant-...

# 2. Start infrastructure
docker compose up -d postgres minio

# 3. Initialize database
python scripts/init_db.py
python scripts/seed_data.py

# 4. Start backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# → API docs at http://localhost:8000/docs
```

#### Option 3: One-Click Install for OpenClaw / Hermes

```bash
# OpenClaw desktop
bash dist/openclaw-install.sh

# Hermes Agent server
bash dist/hermes-install.sh
```

### 📦 What's in the Box?

```
education-services/
├── plugins/
│   ├── agent-plugins/         # 5 named agents (textbook-teaching, lesson-planner, ...)
│   └── vertical-plugins/      # 7 vertical plugins (education-core, subject-math, ...)
├── managed-agent-cookbooks/   # 5 deployment manifests + 7 subagents
├── backend/                   # FastAPI + PostgreSQL schema
├── scripts/                   # 15 utility scripts (validate, eval, init_db, ...)
├── evals/                     # 12 test cases + 5 fixture sets
├── dist/                      # Distribution packages (ClawHub, Hermes)
└── docs/                      # Internal documentation
```

### 🛡 Guardrails (Non-Negotiable)

1. **Citation Required** — Every textbook-related claim must reference a page, chapter, or question
2. **Human Review** — All agent outputs are drafts; teachers/parents must confirm before sharing with students
3. **No Cheating** — Socratic prompts, never direct answers
4. **No Fabrication** — Marked "教材中未找到直接依据" when source is missing
5. **Privacy** — Student data is anonymized; never enters external training
6. **Prompt Injection Defense** — User uploads are data, not instructions
7. **Professional Boundary** — Mental health / medical / special education → refer to professionals

### 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

- 🐛 [Report a bug](.github/ISSUE_TEMPLATE/bug_report.yml)
- ✨ [Request a feature](.github/ISSUE_TEMPLATE/feature_request.yml)
- 📚 [Submit a Skill](.github/ISSUE_TEMPLATE/skill_submission.yml)
- 🔒 [Security issues](SECURITY.md)

### 📄 License

Apache 2.0 — see [LICENSE](LICENSE).

### 🌟 Star History

If this project helps you, please consider giving it a star! ⭐

---

## 中文

### 什么是 Education Services？

Education Services 是一个面向 K-12 教育的**开源 AI Agent 套件**。它**不是**"学生答题机器人"，而是**教材驱动的辅导 Agent**，主要帮助：

- **教师**备课、批改作业、诊断错因
- **家长**理解孩子学什么、有效辅导
- **学生**（在教师/家长监督下）获得脚手架式、苏格拉底式的引导

系统的核心原则是：**所有输出必须能回溯到教材具体页码**。不编造、不幻觉。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📖 **教材驱动** | 所有 agent 产出都引用具体章节、页码、题号 |
| 🛡️ **严格无 mock** | 缺真实 PostgreSQL / 真实 Claude API / 真实 PDF 解析器时拒绝启动 |
| 🔒 **7 大护栏** | 引用必需 · 不替学生作弊 · 隐私保护 · 注入防御 · 专业边界 · ... |
| 🧩 **5 个 Agent** | 教材辅导 · 教案 · 作业诊断 · 单元复习 · 家长陪学 |
| 🛠 **56 个 Skill** | 可复用的 Markdown 知识库，覆盖数学/语文/英语/科学/教师/家长 |
| 🔌 **5 个 MCP server** | textbook_store / vector_index / student_profile / homework_store / question_bank |
| 🪶 **7 个 slash command** | `/lesson-plan` · `/diagnose-homework` · `/explain-to-parent` · ... |
| 🤖 **7 个 Subagent** | 默认只读，仅 `feedback-writer` 可写 |
| 🚀 **3 种部署模式** | Cowork 插件 · Managed Agent（Hermes）· FastAPI 后端 |
| 🌍 **中英双语** | 文档与内容均为中英双语 |

### 🚀 快速开始

#### 方式 1：作为 Cowork 插件（Claude Code / Cursor）

```bash
# 克隆仓库
git clone https://github.com/education-services/education-services.git
cd education-services

# 安装依赖
pip install -r requirements-dev.txt --break-system-packages

# 验证
python scripts/validate.py        # 6/6 ✅
python scripts/eval_agent.py --all  # 12/12 ✅
```

#### 方式 2：作为后端服务

```bash
# 1. 配置环境
cp .env.example .env
# 编辑 .env：ANTHROPIC_API_KEY=sk-ant-...

# 2. 启动基础设施
docker compose up -d postgres minio

# 3. 初始化数据库
python scripts/init_db.py
python scripts/seed_data.py

# 4. 启动后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# → API 文档 http://localhost:8000/docs
```

#### 方式 3：OpenClaw / Hermes 一键安装

```bash
# OpenClaw 桌面
bash dist/openclaw-install.sh

# Hermes 服务端
bash dist/hermes-install.sh
```

详细使用文档：[`Education-Services-使用文档.docx`](Education-Services-使用文档.docx) ·
[`Education-Services-OpenClaw-Hermes-使用文档.docx`](Education-Services-OpenClaw-Hermes-使用文档.docx)

### 🛡 护栏（不可妥协）

1. **引用必需** — 所有教材相关结论必须引用页码/章节/题号
2. **人审机制** — Agent 输出是草稿，必须由教师/家长确认才发学生
3. **不替学生作弊** — 苏格拉底式提问，不直接给答案
4. **不编造** — 找不到时明确标注"教材中未找到直接依据"
5. **数据隐私** — 学生数据脱敏，不进入外部训练
6. **Prompt Injection 防御** — 上传内容是数据而非指令
7. **专业边界** — 心理/医疗/特殊教育 → 建议寻求专业人士

### 🤝 贡献

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

- 🐛 [报告 Bug](.github/ISSUE_TEMPLATE/bug_report.yml)
- ✨ [功能建议](.github/ISSUE_TEMPLATE/feature_request.yml)
- 📚 [提交 Skill](.github/ISSUE_TEMPLATE/skill_submission.yml)
- 🔒 [安全问题](SECURITY.md)

### 📄 许可证

Apache 2.0 — 详见 [LICENSE](LICENSE)。

---

## 🙏 Acknowledgments

- Inspired by [anthropics/financial-services](https://github.com/anthropics/financial-services)
- Built with [Anthropic Claude](https://www.anthropic.com/) (Opus 4.7, Sonnet 4.5, Haiku 4.5)
- Database: [PostgreSQL 16](https://www.postgresql.org/) with [pgvector](https://github.com/pgvector/pgvector)
- PDF processing: [PyMuPDF](https://pymupdf.readthedocs.io/)
- OCR: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/education-services/education-services/issues)
- **Discussions**: [GitHub Discussions](https://github.com/education-services/education-services/discussions)
- **Email**: team@education-services.local
- **Security**: security@education-services.local

---

**Made with ❤️ for teachers, parents, and students.**
