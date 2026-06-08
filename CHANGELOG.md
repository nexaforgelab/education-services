# Changelog

All notable changes to education-services will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### 学科插件
- **subject-english** 完整 plugin（6 个 skills）：vocabulary-builder、grammar-explainer、reading-strategies、writing-rubric、misconception-diagnoser、listening-script、word-problem-builder
- **subject-chinese** 完整 plugin（6 个 skills）：classical-reading、modern-reading-comprehension、writing-rubric、character-lexicon、poetry-appreciation、essay-scaffolder
- **subject-science** 完整 plugin（5 个 skills）：concept-explainer、experiment-guide、misconception-diagnoser、formula-applier、diagram-interpreter

#### 工作流增强
- **teacher-workflow** 增加 5 个 skills：parent-teacher-comm、project-based-homework、exam-deep-analysis、classroom-management-tips、teaching-reflection-log
- **parent-workflow** 增加 4 个 skills：learning-environment-setup、test-anxiety-support、study-habit-builder、parent-teacher-meeting-prep

#### Subagents
- **visualizer** subagent：知识图谱可视化（mermaid / dot / SVG）
- **ocr-recognizer** subagent：作业图片 OCR 识别

#### PDF 处理
- `scripts/ocr_textbook.py`：扫描版教材 OCR（PaddleOCR）
- `scripts/extract_textbook_images.py`：教材图片提取
- `scripts/recognize_formulas.py`：公式识别（pix2tex / Mathpix）

#### LLM 集成
- `scripts/llm_client.py`：Anthropic SDK 客户端（重试、限流、流式）
- `scripts/run_agent_real.py`：真实 Agent 运行（加载 .md prompt + skills + 调用 LLM）

#### 后端增强
- 认证 API（JWT + role-based access control）
- 流式响应（SSE）端点
- WebSocket 端点（实时进度推送）
- 单元测试（pytest）
- 配置文件：security.py、auth.py、streaming.py、websocket.py

#### Eval 测试
- 边界场景测试（grade boundary、empty textbook）
- 安全测试（role boundary、mental health）
- 多语言测试（English output）
- 无障碍测试（visual impairment）

#### 文档
- `docs/api-reference.md`：完整 API 参考
- `docs/deployment.md`：部署指南
- `CONTRIBUTING.md`：贡献指南

#### CI/CD
- GitHub Actions CI workflow（validate + test + eval + lint + build）
- GitHub Actions Deploy workflow
- pre-commit 配置（ruff + prettier + 自定义 hooks）

## [0.1.0] - 2026-06-07

### Added

- 项目初始化
- 1 个主 Agent：textbook-teaching-agent
- 4 个子 Agent：lesson-planner、homework-diagnosis、unit-review、parent-coach
- 2 个 vertical plugin：education-core（6 skills）、subject-math（6 skills）
- 7 个 slash commands
- managed-agent-cookbooks + 5 subagents（feedback-writer 唯一可写）
- 7 个工程化脚本
- 6 个 eval 测试用例
- FastAPI 后端 + PostgreSQL/pgvector schema
- README、architecture、cookbook、guardrails 文档
