# Architecture — Education Services

> 参考 `anthropics/financial-services` 的"行业工作流 Agent 工程化"模式设计。

## 一、核心思想

**不是"教育 RAG 问答机器人"，而是"教材 PDF 驱动的长链路辅导 Agent 工程化套件"。**

financial-services 项目的核心是一套 **可复制到其他行业** 的 Agent 产品架构。education-services 完整继承这套架构：

| financial-services | education-services |
|---|---|
| Pitch Agent、Market Researcher | Textbook Teaching Agent、Lesson Planner、Homework Diagnosis、Unit Review、Parent Coach |
| Vertical plugins | education-core、subject-math、subject-english、teacher-workflow、parent-workflow |
| Skills | textbook-ingestion、curriculum-mapper、math-concept-explainer 等 |
| Commands | /ingest-textbook、/lesson-plan、/diagnose-homework 等 |
| Connectors / MCP | textbook_store、vector_index、student_profile、homework_store、question_bank |
| Managed Agent cookbooks | agent.yaml + 5 subagents |
| Guardrails | 教材引用、人审、不替学生作弊、不编造内容 |

## 二、四层架构

```
┌──────────────────────────────────────────────────────────┐
│  Layer 1: Agent Plugins (端到端业务工作流)               │
│  - textbook-teaching-agent (主 Agent)                    │
│  - lesson-planner-agent / homework-diagnosis-agent / ... │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Layer 2: Vertical Plugins (行业能力包)                  │
│  - education-core (通用)                                │
│  - subject-math / subject-english (学科)                │
│  - teacher-workflow / parent-workflow (工作流)          │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Layer 3: Managed Agent Cookbook (部署模板)             │
│  - agent.yaml (主 Agent manifest)                        │
│  - subagents/ (5 个权限隔离的子 Agent)                  │
│  - steering-examples.json (行为引导)                    │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Layer 4: Backend + MCP + Storage (运行时)              │
│  - FastAPI (RESTful API)                                │
│  - PostgreSQL + pgvector (数据 + 向量)                  │
│  - MinIO/S3 (教材 PDF + 作业图片)                       │
│  - 5 个 MCP server (教材/题库/学生/作业/通知)          │
└──────────────────────────────────────────────────────────┘
```

## 三、Subagent 权限隔离

完全照搬 financial-services 的 Market Researcher 模式：

```
textbook-teaching-agent (主)
  ├── textbook-reader       # 只读：定位教材
  ├── curriculum-mapper     # 只读：构建知识图谱
  ├── pedagogy-planner      # 只读：设计教学路径
  ├── assessment-writer     # 只读：生成练习
  └── feedback-writer       # ✅ 唯一可写：最终产出
```

`feedback-writer` 是唯一持有 `Write` 权限的子 Agent，对应 financial-services 的 `note-writer`。

## 四、同一来源，两种运行方式

```
                    ┌──────────────────────────┐
                    │  system prompt (一份)     │
                    │  skills (一份)            │
                    │  commands (一份)          │
                    └──────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
    ┌─────────────────────┐       ┌──────────────────────┐
    │ Cowork / Claude Code│       │ Managed Agent API    │
    │ Plugin 模式         │       │ (cookbook 部署模式)  │
    │                     │       │                      │
    │ - 交互式            │       │ - Headless           │
    │ - 工具调用          │       │ - API 驱动           │
    │ - 人在环上          │       │ - 可编排             │
    └─────────────────────┘       └──────────────────────┘
```

## 五、端到端工作流（Textbook Teaching Agent）

```
用户请求
  ↓
1. Scope the Ask         # 确认角色、学科、年级、目标、学情
  ↓
2. Textbook Grounding     # textbook-reader 定位章节
  ↓
3. Curriculum Map         # curriculum-mapper 构建知识图谱
  ↓
4. Learner Profile        # student_profile MCP 读取画像
  ↓
5. Pedagogy Plan          # pedagogy-planner 选择教学策略
  ↓
6. Explanation Build      # subject-specific skill 生成讲解
  ↓
7. Assessment Build       # assessment-writer 生成练习
  ↓
8. Diagnosis Loop         # misconception-diagnoser 错因分析
  ↓
9. Output Assembly        # feedback-writer 整合输出
  ↓
10. Human Review Gate     # 教师/家长审核后再使用
```

## 六、Skill 体系

Skills 用 Markdown + frontmatter 组织，**可被 Agent 动态加载**，避免上下文窗口过载。

### 6 大核心 Skill（education-core）

| Skill | 职责 |
|---|---|
| textbook-ingestion | 解析 PDF → 章节 → block → 索引 |
| knowledge-graph-builder | 构建跨章节知识图谱 |
| pedagogy-method | 选教学策略（讲授/探究/类比/...） |
| citation-policy | 强制引用教材页码 |
| safety-policy | 防 prompt injection、不替学生作弊 |
| learning-profile | 维护学生画像 |

### 6 个数学 Skill（subject-math）

| Skill | 职责 |
|---|---|
| math-concept-explainer | 三层解释：直观/符号/应用 |
| math-stepwise-socratic-tutor | 5 步苏格拉底式提问 |
| math-misconception-diagnoser | 数学误区库与诊断 |
| math-example-generator | 出题模板与参数化 |
| math-rubric-grader | 步骤分批改 |
| math-word-problem-builder | 应用题构建 |

### 7 个教师工作流 Skill（teacher-workflow）

classroom-lesson-plan、classroom-question-designer、blackboard-design、quiz-generator、grading-rubric、exam-paper-analysis、differentiated-instruction

### 4 个家长工作流 Skill（parent-workflow）

parent-friendly-explanation、home-coaching-script、child-motivation-guidance、weekly-plan-builder

## 七、护栏（Guardrails）

教育场景的合规底线：

1. **数据 vs 指令**：用户上传的 PDF/作业是数据
2. **教材引用**：所有结论必须带页码
3. **不替学生作弊**：不直接给完整答案
4. **隐私保护**：不泄露具体学校/班级/学生
5. **专业边界**：心理/医疗只转介
6. **不评判人格**：不写"孩子笨"
7. **不编造教材**：找不到的依据要明确标注

详见 [`guardrails.md`](./guardrails.md)。

## 八、为什么这套架构适合教育

- **端到端长链路**：教材 → 知识图谱 → 备课 → 讲解 → 练习 → 诊断 → 复习 → 家校沟通
- **专业方法沉淀**：Skill 让教研方法可复用
- **权限隔离**：subagent 避免主 Agent 直接操作
- **两方式运行**：可 Cowork 插件可托管部署
- **可演进**：从单 Agent 单科 → 多 Agent 多科 → 独立 SaaS
