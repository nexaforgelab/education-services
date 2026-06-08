# Release Notes — v0.1.0

> 🎉 **First public release of Education Services**
> Released: 2026-06-08 · Apache 2.0 License

We're excited to announce the first public release of **Education Services** — an open-source AI agent pack for textbook-driven K-12 education!

## 🌟 What's New

This is our **MVP release**, focused on validating the architecture and core workflows. It includes:

### 📚 Core Capabilities
- **5 named agents** that solve real teaching and parenting problems
- **56 reusable Skills** (Markdown knowledge bases) for math, Chinese, English, science, teacher workflow, and parent workflow
- **7 slash commands** for the most common workflows
- **FastAPI backend** with PostgreSQL + pgvector for textbook indexing

### 🤖 The 5 Agents

| Agent | What it does |
|-------|--------------|
| 📖 **Textbook Teaching Agent** | The main agent — takes a textbook PDF + user goal, produces complete tutoring artifacts |
| 👩‍🏫 **Lesson Planner Agent** | Generates 45/60/90-minute lesson plans with board design, question chain, differentiated tasks, and homework |
| 🔍 **Homework Diagnosis Agent** | Analyzes wrong answers, classifies error types, provides 1-on-1 explanation, variant questions, and review suggestions |
| 📝 **Unit Review Agent** | Builds knowledge network, identifies high-frequency test points, common errors, and tiered practice |
| 👨‍👩‍👧 **Parent Coach Agent** | Translates teacher-language into parent-language that parents can use to tutor their children |

### 🛡 7 Non-Negotiable Guardrails

Built into every agent's system prompt:
1. **Citation Required** — Every claim traces to a specific page
2. **Human Review** — All outputs are drafts
3. **No Cheating** — Socratic prompts, never direct answers
4. **No Fabrication** — Marked when source is missing
5. **Privacy** — Student data is anonymized
6. **Prompt Injection Defense** — User uploads are data, not instructions
7. **Professional Boundary** — Mental/medical/special-ed → refer to professionals

### 🚀 3 Deployment Modes

- **Cowork Plugin** — Install as a Claude Code / Cursor plugin
- **Managed Agent** — Deploy via OpenClaw / Hermes bundle
- **FastAPI Backend** — Standalone HTTP/WebSocket service

## 📦 What's in This Release

```
education-services-0.1.0/
├── 195 tracked files
├── 326 individual files
├── 1.5 MB git repository
├── 100% open-source (Apache 2.0)
└── Bilingual documentation (English + 中文)
```

### File Breakdown

| Category | Count |
|----------|-------|
| Plugin files (plugins.json, SKILL.md) | 56 |
| Agent cookbooks (agent.yaml) | 5 |
| Subagent manifests (subagent.yaml) | 7 |
| Backend Python files | 11 |
| Top-level scripts | 15 |
| Eval test cases | 12 |
| Eval fixtures | 13 |
| Documentation (.md) | 7 |
| Documentation (.docx) | 2 |
| GitHub community files | 9 |

## 📊 Quality Metrics

| Metric | Status |
|--------|--------|
| `python scripts/validate.py` | ✅ 6/6 |
| `python scripts/eval_agent.py --all` | ✅ 12/12 |
| Backend tests | ✅ Passes (with skip-on-missing-deps) |
| `ruff check` | ✅ Clean |
| Mock dependencies | ❌ None (strict mode) |

## 🚀 Getting Started

### Install (5 minutes)

```bash
# Clone
git clone https://github.com/yourname/education-services.git
cd education-services

# Install Python dependencies
pip install -r requirements-dev.txt --break-system-packages

# Verify project structure
python scripts/validate.py        # Should pass 6/6
python scripts/eval_agent.py --all  # Should pass 12/12
```

### Run the Backend (10 minutes)

```bash
# 1. Configure
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY=sk-ant-...

# 2. Start infrastructure
docker compose up -d postgres minio

# 3. Initialize database
python scripts/init_db.py
python scripts/seed_data.py

# 4. Start API server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Use as OpenClaw / Hermes Bundle

```bash
# OpenClaw
bash dist/openclaw-install.sh

# Hermes
bash dist/hermes-install.sh
```

## ⚠️ Known Limitations

This is an MVP, so please be aware of:

1. **Math focus** — Subject coverage is deepest for math. Chinese/English/science are present but less developed.
2. **Real services required** — Will NOT start with mocked or missing dependencies. This is by design.
3. **No production multi-tenancy** — Single-tenant only. For production multi-school, see Roadmap.
4. **English & Chinese content** — Both languages are supported, but Chinese is the primary authoring language.
5. **No LMS integration** — Direct integration with Canvas/Moodle/ClassIn is in Roadmap.
6. **Web UI is minimal** — Currently a FastAPI auto-generated Swagger UI. Custom UI is in Roadmap.

## 🗺 Roadmap

### v0.2 (Q3 2026)
- [ ] Add Lesson Planner / Homework Diagnosis as fully separate deployable agents
- [ ] Improve Chinese subject coverage (诗词鉴赏深度、作文评分)
- [ ] Add visual learning content (diagrams, mind maps)
- [ ] Basic multi-tenancy (school-level isolation)

### v0.3 (Q4 2026)
- [ ] English subject depth (writing rubric, vocabulary)
- [ ] WebSocket progress streaming
- [ ] Custom knowledge point tagging

### v0.4 (Q1 2027)
- [ ] LMS / ClassIn / DingTalk integration
- [ ] Student progress dashboard
- [ ] Voice input for homework (Whisper integration)

### v0.5 (Q2 2027)
- [ ] Managed multi-school SaaS mode
- [ ] On-premise deployment package (Helm chart)
- [ ] Native mobile apps

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md).

Top contribution areas:
- 📚 **New Skills** (use [skill submission template](../.github/ISSUE_TEMPLATE/skill_submission.yml))
- 🌐 **New subject coverage** (physics, history, geography)
- 🔌 **New MCP server integrations**
- 🐛 **Bug reports and fixes**
- 📖 **Documentation improvements** (English translation help especially welcome!)

## 🙏 Acknowledgments

- Inspired by [anthropics/financial-services](https://github.com/anthropics/financial-services)
- Built on [Anthropic Claude](https://www.anthropic.com/) (Opus 4.7, Sonnet 4.5, Haiku 4.5)
- Powered by [PostgreSQL 16](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector)

## 📞 Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourname/education-services/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/yourname/education-services/discussions)
- **Email**: team@education-services.local
- **Security**: security@education-services.local

---

## 📝 Upgrade Path

This is the first release, so no upgrade path is needed.

For future releases, see [CHANGELOG.md](../CHANGELOG.md) and follow the migration notes in each release.

## 🔒 Security

See [SECURITY.md](../SECURITY.md) for our security policy and how to report vulnerabilities.

## 📄 License

Apache 2.0 — see [LICENSE](../LICENSE).

---

**⭐ If you find this useful, please star the repo!**
