---
name: lesson-plan
description: 生成教师教案、课堂活动、板书、小测和作业。
usage: /lesson-plan <chapter> <duration> <student_level>
---

# /lesson-plan 命令

为教师生成指定章节的完整教案。

## 语法

```
/lesson-plan <chapter> <duration> <student_level>
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| chapter | ✅ | 章节名（中文 / 章节 ID） |
| duration | ✅ | 45 / 60 / 90 |
| student_level | ✅ | 基础薄弱 / 中等 / 拔高 / 混合 |

## 行为

调用 `lesson-planner` skill 和 `curriculum-mapper` skill：

1. 定位教材章节
2. 构建知识图谱
3. 选择教学策略
4. 生成教案
5. 配套板书、提问链、分层任务、作业

## 输出

```
out/lesson_plan/
├── lesson_plan.md          # 主教案
├── board_design.md         # 板书
├── question_chain.md       # 提问链
├── differentiated_tasks.md # 分层任务
├── worksheet_basic.md      # 基础练习
├── worksheet_advanced.md   # 提高练习
├── homework.md             # 作业
└── reflection_template.md  # 教学反思模板
```

## 质量保证

- 时长严格匹配 `duration`
- 例题 100% 引用教材页码
- 提问链覆盖 4 类（复习 / 理解 / 应用 / 评价）
- 教学反思模板可课后填写

## 示例

```
/lesson-plan 有理数加减法 45 中等
```

## 关联

- 调用主 Agent：`textbook-teaching-agent`
- 调用 subagent：`textbook-reader`, `curriculum-mapper`, `pedagogy-planner`, `assessment-writer`, `feedback-writer`
