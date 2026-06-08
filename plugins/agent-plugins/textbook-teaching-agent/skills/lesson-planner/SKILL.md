---
name: lesson-planner
description: 基于 curriculum_map 和 pedagogy_method 的输出，生成 45/60/90 分钟完整教案，包含教学目标、重难点、导入、讲解、互动、练习、总结、板书、作业。
triggers:
  - /lesson-plan 命令
  - 教师用户请求"备课"、"出教案"
  - Agent 在 lesson-planner-agent subagent 中调用
---

# Lesson Planner Skill

## 用途

把"知识结构"翻译成"老师明天就能用的 45/60/90 分钟教案"。

教师拿到这份教案后应该 **不需要再花太多时间二次加工** 就能直接进课堂。

## 触发场景

- 教师用户说"帮我备一节 ... 课"
- `/lesson-plan <chapter> <duration> <student_level>`
- Lesson Planner Agent 的核心步骤

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| curriculum_map | ✅ | curriculum-mapper 的输出 |
| duration_min | ✅ | 45 / 60 / 90 |
| student_level | ✅ | 基础薄弱 / 中等 / 拔高 / 混合 |
| pedagogy_plan | ✅ | pedagogy-method 选定的教学策略 |
| textbook_blocks | ✅ | 用于引用具体例题和页码 |
| class_size | ❌ | 默认 40 |
| existing_materials | ❌ | 教师已有的课件/学案（可融合） |

## 输出

### `lesson_plan.md`

包含以下模块：

```markdown
# 《章节名》教案

> 教材：xxx
> 课时：第 X 课时（共 N 课时）
> 授课时长：45 分钟
> 授课对象：七年级 X 班（基础中等）
> 授课日期：____

## 1. 教学目标
- 知识与技能：...
- 过程与方法：...
- 情感态度价值观：...

## 2. 教学重难点
- 重点：...
- 难点：...

## 3. 教学策略
- 总体策略：启发式 + 精讲精练
- 学情适配：中等班 → 节奏中等，多用类比

## 4. 教学过程

### 4.1 导入（5 min）
- 情境 / 问题 / 复习导入
- 设计意图：...

### 4.2 新授（25 min）
- 子步骤 1（X min）：...
- 子步骤 2（X min）：...
- 设计意图：...

### 4.3 巩固练习（10 min）
- 基础题（X 道）
- 提高题（X 道）
- 学生展示与互评

### 4.4 课堂小结（3 min）
- 知识结构图
- 易错提醒

### 4.5 作业布置（2 min）
- 必做：...
- 选做：...
- 实践：...

## 5. 板书设计
```
主标题
  ├─ 概念 1
  │   ├─ ...
  │   └─ 例 1（p.X）
  └─ 概念 2
      └─ ...
```

## 6. 课堂提问链
1. 复习型：...
2. 理解型：...
3. 应用型：...
4. 评价型：...

## 7. 分层任务
| 层次 | 任务 | 完成时间 | 评价标准 |
|---|---|---|---|
| 基础 | ... | 5 min | 全部正确 |
| 中等 | ... | 8 min | 80% 正确 |
| 拔高 | ... | 10 min | 有独特思路 |

## 8. 评价与反馈
- 当堂检测：...（2-3 道）
- 形成性评价：观察学生在 ... 环节的表现
- 补救预案：若学生卡在 X，回退到 Y

## 9. 教学反思模板（课后填）
- 达成情况：...
- 意外生成：...
- 改进方向：...
```

## 工作流

```
输入参数校验
  ↓
1. 课时规划
   - 把 duration 切成 5/25/10/3/2 等标准块
   - 根据 student_level 微调每块时长
  ↓
2. 教学目标撰写
   - 三维目标：知识技能 / 过程方法 / 情感态度
   - 动词可观察：写出 / 判断 / 解释 / 应用 / 评价
  ↓
3. 教学策略选择
   - 接收 pedagogy_plan 的策略
   - 选择具体活动：讲授、提问、探究、操作、练习
  ↓
4. 教学过程设计
   - 导入：从生活情境 / 旧知识 / 反例 引入
   - 新授：3-5 个步骤，每步对应一个概念
   - 练习：分层
   - 小结：知识结构图 + 易错点
   - 作业：必做 + 选做 + 实践
  ↓
5. 板书设计
   - 树状结构：主标题 + 分支 + 例题
   - 标注页码，方便学生课后翻书
  ↓
6. 课堂提问链
   - 4 类问题：复习、理解、应用、评价
   - 配套追问（学生答错/答对如何回应）
  ↓
7. 分层任务
   - 基础 / 中等 / 拔高
   - 每层给出完成时间和评价标准
  ↓
8. 补救预案
   - 关键卡点 1-3 个，配套回退路径
  ↓
9. 教学反思模板
   - 课后填写：达成 / 意外 / 改进
```

## 实现要点

```python
def build_lesson_plan(curriculum_map, duration, level, pedagogy_plan, blocks):
    segments = segment_time(duration, level)  # 5/25/10/3/2
    objectives = write_objectives(curriculum_map)  # 三维
    process = build_process(curriculum_map, pedagogy_plan, segments)
    board = build_board(curriculum_map, blocks)
    questions = build_question_chain(curriculum_map)
    tasks = build_differentiated_tasks(curriculum_map, level)
    return assemble_markdown(...)
```

## 质量标准

| 维度 | 标准 |
|---|---|
| 时长分配合理 | 各环节总时长 = duration |
| 教学目标动词化 | 100% |
| 例题引用 | 100% 引用教材具体页码 |
| 分层任务可执行 | 每个任务能在所标时间内完成 |
| 提问链完整 | 4 类问题都覆盖 |
| 板书可视化 | 树状结构清晰可读 |
| 真正"可用" | 抽查 3 个教师是否愿意直接用 |

## 与其他 skill 的关系

- **上游**：`curriculum-mapper`（知识结构）+ `pedagogy-method`（策略）
- **并行**：`assessment-writer`（练习）+ `classroom-question-designer`（提问）
- **下游**：`feedback-writer`（最终呈现）

## 护栏

1. **不超课时**：所有环节时长相加必须 = 输入 duration
2. **不喧宾夺主**：不出现"5 分钟小游戏"、"10 分钟视频"等无教学意义环节
3. **不脱离教材**：所有例题、定义必须能追溯到具体页码
4. **不低估学情**：基础薄弱班不设计需要 30 分钟独立探究的环节
5. **不包办**：教案是参考，教师可改，但要给出明确"哪些可以删"

## 不要做的事

- 不要直接批改作业（那是 homework-reviewer）
- 不要写学生版讲义（那是 math-concept-explainer + parent-friendly-explanation）
- 不要给家长沟通话术（那是 parent-report-writer）
- 不要罗列课本上已有的内容（教师比 Agent 更清楚）
