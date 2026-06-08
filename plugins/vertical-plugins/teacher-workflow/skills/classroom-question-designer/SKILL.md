---
name: classroom-question-designer
description: 生成课堂提问链：复习型、理解型、应用型、评价型，配套追问与回退策略。
triggers:
  - 教案生成需要提问链
  - 教师问"这节课怎么问"
---

# Classroom Question Designer Skill

## 用途

设计 4 类课堂提问，覆盖布鲁姆认知层级（记忆 / 理解 / 应用 / 评价）。

## 4 类问题

| 类型 | 目的 | 动词 | 示例 |
|---|---|---|---|
| 复习型 | 唤起旧知 | 回忆、复述 | "上节课我们学了什么？" |
| 理解型 | 检验理解 | 解释、归纳 | "为什么 -(-2) = 2？" |
| 应用型 | 学以致用 | 应用、计算 | "用今天的方法计算这题" |
| 评价型 | 高阶思维 | 评价、辨析 | "哪种方法更好？为什么？" |

## 输出

```yaml
question_chain:
  - id: q01
    type: 复习
    stem: "上节课我们学了什么？"
    expected_response: "正负数"
    fallback: "翻到教材第 2 页，看一下"
  - id: q02
    type: 理解
    stem: "-3 + 5 怎么算？为什么结果是正数？"
    expected_response: "异号相加，绝对值相减，取大号"
    fallback: "看数轴上 -3 和 5 谁更远"
  - id: q03
    type: 应用
    stem: "用今天的方法计算 -7 - (-3)"
    expected_response: "-7 + 3 = -4"
    fallback: "先变符号，再算"
  - id: q04
    type: 评价
    stem: "看黑板上的三种方法，哪种最简洁？"
    expected_response: "第二种"
    fallback: "数步骤数"
```

## 质量标准

- 4 类都有
- 难度递进
- 每题有 fallback
- 配套追问
