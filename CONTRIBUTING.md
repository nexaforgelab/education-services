# Education Services — 贡献指南

## 一、欢迎

感谢您对 education-services 的关注！

这是一个教育 AI Agent 项目，参考 Anthropic financial-services 架构，主要面向教师和家长的教材 PDF 驱动辅导。

## 二、贡献方式

### 1. 报告 Bug

- 在 [Issues](https://github.com/your-org/education-services/issues) 提交
- 提供：复现步骤、预期、实际、环境信息
- 用模板：bug_report.md

### 2. 提出新功能

- 在 [Issues](https://github.com/your-org/education-services/issues) 提交
- 用模板：feature_request.md
- 详细说明：使用场景、优先级、可能影响

### 3. 提交代码

- Fork 仓库
- 创建分支：`git checkout -b feature/xxx`
- 提交：`git commit -m 'feat: xxx'`
- 推送：`git push origin feature/xxx`
- 创建 PR

### 4. 改进文档

- 修正错别字
- 补充示例
- 翻译其他语言

### 5. 添加 Skill / Agent

按仓库规范：
- 新 Skill：`vertical-plugins/<plugin>/skills/<skill>/SKILL.md`
- 新 Agent：`agent-plugins/<slug>/` + `managed-agent-cookbooks/<slug>/`
- 运行 `python scripts/sync-agent-skills.py --sync` 同步
- 运行 `python scripts/validate.py` 验证

## 三、代码规范

### Python

- 用 `black` 格式化：`black .`
- 用 `ruff` 检查：`ruff check .`
- 用 `mypy` 类型检查：`mypy .`
- 风格：PEP 8
- docstring：Google 风格

### Markdown / YAML

- 用 prettier 格式化
- YAML 用 2 空格缩进
- Markdown 用 ATX 风格标题（`#`）

### Commit 信息

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新功能
fix: 修复
docs: 文档
style: 格式
refactor: 重构
test: 测试
chore: 构建
```

示例：
```
feat(math): 增加一元二次方程 skill
fix(textbook-ingestion): 修复 PDF 加密检测
docs: 更新 deployment 文档
```

## 四、PR 流程

### 1. 检查清单

提交 PR 前：

- [ ] 代码格式化（black / prettier）
- [ ] 通过 linting（ruff / eslint）
- [ ] 添加测试（如适用）
- [ ] 更新文档（如适用）
- [ ] 通过 `python scripts/validate.py`
- [ ] 通过相关 `pytest`

### 2. PR 模板

```markdown
## 描述
（说明这个 PR 做什么）

## 关联 Issue
（如果有）

## 改动
- 改动 1
- 改动 2

## 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试

## 截图 / 录屏
（如适用）
```

### 3. Code Review

- 至少 1 个 maintainer 审查
- 通过 CI
- 通过对话解决反馈

## 五、本地开发

### 1. 环境

```bash
# Python 3.11+
python --version

# 安装依赖
cd backend
pip install -r requirements.txt --break-system-packages
pip install -r requirements-dev.txt --break-system-packages
```

### 2. Pre-commit

```bash
# 安装
pip install pre-commit --break-system-packages
pre-commit install

# 手动运行
pre-commit run --all-files
```

### 3. 测试

```bash
# 单元测试
cd backend && pytest

# 集成测试
pytest tests/integration/

# Evals
cd .. && python scripts/eval_agent.py --all
```

### 4. 校验

```bash
# 结构校验
python scripts/validate.py

# 同步 skill
python scripts/sync-agent-skills.py --check
```

## 六、添加新 Skill

### 1. 位置

`vertical-plugins/<plugin>/skills/<skill-name>/SKILL.md`

### 2. Frontmatter 模板

```markdown
---
name: skill-name
description: 一句话说明
triggers:
  - 触发场景 1
  - 触发场景 2
---

# Skill Name

## 用途
（详细说明）

## 触发场景
- 场景 1
- 场景 2

## 输入
| 字段 | 必填 | 说明 |
|---|---|---|
| ... | ✅ | ... |

## 输出
（输出结构）

## 工作流
（流程图 / 步骤）

## 质量标准
- 标准 1
- 标准 2

## 护栏
1. 护栏 1
2. 护栏 2

## 不要做的事
- 不要 1
- 不要 2
```

### 3. 同步到 Agent

编辑对应 Agent 的 `plugin.json`：
```json
{
  "skills": [
    "./skills/your-new-skill/SKILL.md"
  ]
}
```

或运行：
```bash
python scripts/sync-agent-skills.py --sync
```

## 七、添加新 Agent

### 1. 创建 agent-plugins/<slug>/

```
agent-plugins/<slug>/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── <slug>-agent.md
└── skills/  # 可选
    └── ...
```

### 2. 创建 managed-agent-cookbooks/<slug>/

```
managed-agent-cookbooks/<slug>/
├── agent.yaml
├── README.md
├── steering-examples.json
└── subagents/  # 可选
    └── ...
```

### 3. 校验

```bash
python scripts/validate.py
```

## 八、添加 Eval 测试

### 1. 位置

`evals/test_cases/<category>/<test-name>.yaml`

### 2. 模板

```yaml
id: test_id
name: 测试名
description: |
  测试描述
category: category_name
fixture: evals/fixtures/...

input:
  command: /command-name
  args: [...]
  user_role: teacher

expected:
  must_contain: [...]
  must_not_contain: [...]

checks:
  check_citation: true
  check_no_unsourced: true
  check_no_personal_judgments: true
  check_no_direct_cheating: true

severity: high
```

## 九、版本发布

### 1. SemVer

- MAJOR：不兼容 API 变更
- MINOR：向下兼容新功能
- PATCH：向下兼容 bug 修复

### 2. Changelog

每个版本写 changelog：

```markdown
## [1.0.0] - 2026-07-01
### Added
- 完整的多 Agent 体系
- 4 学科覆盖

### Changed
- 优化 PDF 解析速度

### Fixed
- 修复 XSS 漏洞
```

## 十、Code of Conduct

### 我们承诺

- 欢迎所有背景的贡献者
- 尊重不同观点
- 接受建设性批评
- 关注社区最佳利益

### 不可接受

- 骚扰 / 歧视
- 公开 / 私下侮辱
- 未经允许发布他人隐私
- 其他不专业行为

## 十一、联系我们

- Issues：https://github.com/your-org/education-services/issues
- Discussions：https://github.com/your-org/education-services/discussions
- Email：team@education-services.local

## 十二、许可证

贡献的代码采用 Apache 2.0 许可证。
