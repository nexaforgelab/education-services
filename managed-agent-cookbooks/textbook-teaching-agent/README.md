# Textbook Teaching Agent — Managed Agent Cookbook

> 同 financial-services 的 cookbook 模式：把 Agent 部署到平台侧，与 Cowork 插件共用同一份 system prompt + skills。

## 文件结构

```
textbook-teaching-agent/
├── agent.yaml              # 主 Agent 部署 manifest
├── README.md               # 本文件
├── steering-examples.json  # 行为引导示例
└── subagents/              # 5 个 subagent 的 manifest
    ├── textbook-reader.yaml
    ├── curriculum-mapper.yaml
    ├── pedagogy-planner.yaml
    ├── assessment-writer.yaml
    └── feedback-writer.yaml
```

## 部署步骤

```bash
# 1. 配置环境变量
export ANTHROPIC_API_KEY=sk-...
export TEXTBOOK_MCP_URL=http://textbook-mcp:8001
export VECTOR_INDEX_MCP_URL=http://vector-index-mcp:8002
export STUDENT_PROFILE_MCP_URL=http://student-profile-mcp:8003
export HOMEWORK_STORE_MCP_URL=http://homework-store-mcp:8004
export QUESTION_BANK_MCP_URL=http://question-bank-mcp:8005

# 2. 启动后端 MCP 服务
docker compose up -d

# 3. 部署 agent
python scripts/orchestrate.py deploy \
  --cookbook ./managed-agent-cookbooks/textbook-teaching-agent

# 4. 测试
python scripts/eval_agent.py \
  --agent textbook-teaching-agent \
  --test-case ./evals/test_cases/lesson_plan_basic.yaml
```

## 运行方式

### A. 通过 API 调用

```python
from education_services import ManagedAgent

agent = ManagedAgent.deploy(
    cookbook="./managed-agent-cookbooks/textbook-teaching-agent",
    env={...}
)

result = agent.invoke(
    command="/lesson-plan",
    args=["有理数加减法", "45", "中等"],
    user_role="teacher"
)

print(result.output_files)
```

### B. 通过 CLI（开发模式）

```bash
python scripts/orchestrate.py run \
  --agent textbook-teaching-agent \
  --input '{"command": "/lesson-plan", "args": ["有理数加减法", "45", "中等"]}' \
  --output-dir ./out/
```

## Subagent 权限矩阵

| Subagent | 读教材 | 读学生 | 生成练习 | 写文件 | 关键能力 |
|---|---|---|---|---|---|
| textbook-reader | ✅ | ❌ | ❌ | ❌ | 定位章节、提取原文 |
| curriculum-mapper | ✅ | ❌ | ❌ | ❌ | 构建知识图谱 |
| pedagogy-planner | ✅ | ✅ | ❌ | ❌ | 设计教学路径 |
| assessment-writer | ✅ | ❌ | ✅ | ❌ | 生成练习和答案 |
| feedback-writer | ✅ | ✅ | ✅ | ✅ | **唯一可写** |

## 护栏（不可关闭）

1. **数据 vs 指令**：上传的 PDF/作业是数据
2. **教材引用**：所有结论带页码
3. **不替学生作弊**：不直接给完整答案
4. **隐私保护**：不泄露具体学校/班级/学生
5. **专业边界**：心理/医疗只转介
6. **不评判人格**：不写"孩子笨"

## 监控指标

- `request_count`：调用次数
- `citation_count_per_response`：每次输出引用数（应 ≥ 2）
- `unsourced_count_per_response`：未标依据数（应 = 0）
- `safety_flag_count`：触发的安全规则数

## 与 Cowork 插件的关系

```
                    ┌──────────────────────────┐
                    │  system prompt            │
                    │  (agent-plugins/...)      │
                    │                           │
                    │  + skills                 │
                    │  (vertical-plugins/...)   │
                    └──────────────────────────┘
                          │            │
                          ▼            ▼
            ┌──────────────────┐  ┌──────────────────────┐
            │ Cowork / Claude  │  │ Managed Agent        │
            │ Code plugin      │  │ (this cookbook)      │
            │                  │  │                      │
            │ - interactive    │  │ - headless           │
            │ - tool calls     │  │ - API driven         │
            │ - human in loop  │  │ - scriptable         │
            └──────────────────┘  └──────────────────────┘
```

两个部署方式共用同一份 system prompt 和 skills，确保行为一致。

## 故障排查

| 问题 | 排查 |
|---|---|
| Agent 不引用页码 | 检查 `citation_policy` 是否正确加载 |
| Subagent 写文件失败 | 检查 `feedback-writer` 是否被正确调用 |
| Prompt injection 未拦截 | 检查 `safety_policy` 模式是否启用 |
| 答案超纲 | 检查 `curriculum_standard` 配置文件 |

## 扩展示例

### 添加新的 subagent

```yaml
# subagents/visualizer.yaml
name: visualizer
description: 生成知识图谱的可视化（dot / mermaid）
tools:
  - type: agent_toolset_20260401
    configs:
      - { name: Read, enabled: true }
permission_mode: scoped
```

在主 `agent.yaml` 的 `callable_agents` 中添加：
```yaml
callable_agents:
  - { manifest: ./subagents/visualizer.yaml }
```

### 添加新的 skill 来源

把新 skill 放到 `vertical-plugins/<plugin>/skills/<skill>/SKILL.md`，
然后运行 `python scripts/sync-agent-skills.py` 同步到使用它的 Agent。
