---
name: quiz-generator
description: 生成课堂小测：5-10 分钟，覆盖刚讲的核心概念，含答案。
triggers:
  - 教案需要课堂小测
  - 教师说"出个小测"
---

# Quiz Generator Skill

## 用途

快速生成 5-10 分钟课堂小测，检验本节核心概念。

## 输出

```yaml
quiz:
  title: "1.3 有理数加减法 课堂小测"
  duration_min: 8
  total_score: 100
  questions:
    - id: q1
      type: choice
      score: 20
      stem: "下列计算正确的是（   ）"
      options: ["A. -3+5=-2", "B. -3-5=2", "C. -3-(-5)=2", "D. 3-(-5)=-2"]
      answer: C
    - id: q2
      type: fill
      score: 20
      stem: "(-7) + 3 = ____"
      answer: -4
    - id: q3
      type: short_answer
      score: 30
      stem: "计算 |3-5| + (-2) - 1"
      answer: "0"
      steps: "1) |3-5|=2  2) 2+(-2)-1 = -1"
    - id: q4
      type: application
      score: 30
      stem: "某地白天 5°C，夜间 -3°C，温差是多少？"
      answer: "8°C"
      steps: "5 - (-3) = 8"
```

## 质量标准

- 时长 5-10 min
- 覆盖 3-5 个核心概念
- 难度中等偏易
- 答案可验
- 配套步骤
