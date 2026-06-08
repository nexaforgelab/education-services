---
name: unit-review
description: 生成单元复习资料、知识网络、易错点、测试卷。
usage: /unit-review <unit> [duration_days]
---

# /unit-review 命令

为单元复习生成系统化复习资料。

## 语法

```
/unit-review <unit> [duration_days]
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| unit | ✅ | 单元名（章节列表 / 单元 ID） |
| duration_days | ❌ | 复习时长，默认 7 天 |

## 行为

调用 `unit-review-agent` 及其子 skill：

1. 拉取单元所有章节
2. 构建跨章节知识图谱
3. 标注高频考点
4. 拉易错点
5. 生成分层测试卷
6. 生成复习计划

## 输出

```
out/unit_review/
├── README.md              # 单元总览
├── knowledge_graph.md     # 知识网络
├── key_points.md          # 高频考点
├── common_mistakes.md     # 易错点
├── review_plan.md         # 复习计划
├── exam_paper_v1.md       # 基础卷
├── exam_paper_v2.md       # 提高卷
├── exam_paper_v3.md       # 综合卷
├── answers.md             # 参考答案
└── pre_exam_tips.md       # 考前提醒
```

## 高频考点标注

- ★★★：5 年 5 次（必考）
- ★★：5 年 2-4 次（高频）
- ★：5 年 1 次或新增考点

## 质量保证

- 考点不超纲
- 测试卷 60-90 分钟
- 复习计划每天 30-60 分钟
- 不制造焦虑

## 示例

```
/unit-review 有理数整章 7
/unit-review 一元一次方程 5
```

## 边界

- 不替学生应试
- 不写"考试技巧"违反诚信
- 不制造焦虑
- 不强推某种记忆法
