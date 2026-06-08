---
name: classroom-lesson-plan
description: 教师工作流 skill：基于 knowledge-graph-builder 输出生成完整课堂教案，含教学目标、重难点、导入、新授、练习、小结、作业。
triggers:
  - /lesson-plan 命令
  - lesson-planner-agent 调用的核心 skill
  - 教师说"帮我备课"
---

# Classroom Lesson Plan Skill

## 用途

把"知识结构"翻译成"老师明天就能用的 45/60/90 分钟教案"。

## 输出结构

```markdown
# 《章节名》教案

> 教材：xxx | 时长：45 min | 对象：七年级 X 班 | 水平：中等

## 1. 教学目标（三维）
## 2. 教学重难点（含页码依据）
## 3. 教学策略
## 4. 教学过程
   - 4.1 导入（5 min）
   - 4.2 新授（25 min）
   - 4.3 巩固练习（10 min）
   - 4.4 课堂小结（3 min）
   - 4.5 作业布置（2 min）
## 5. 板书设计
## 6. 课堂提问链（4 类）
## 7. 分层任务
## 8. 评价与反馈
## 9. 补救预案
## 10. 教学反思模板
```

## 质量标准

- 时长分配合理，总和 = 输入 duration
- 100% 例题引用教材页码
- 4 类提问齐备
- 分层任务可执行
- 板书可视化

## 详细文档

完整实现见 `agent-plugins/textbook-teaching-agent/skills/lesson-planner/SKILL.md`
（textbook-teaching-agent 与 lesson-planner-agent 共用同一份教案生成逻辑）
