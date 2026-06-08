---
name: grading-rubric
description: 通用批改 rubric 生成：步骤分、结果分、表达分。
triggers:
  - worksheet-generator 需要 rubric
  - 教师需要标准化评分
---

# Grading Rubric Skill

## 用途

为教师提供 **可重复使用的批改标准**——按步骤分、按结果分、按表达分。

## 数学题 Rubric 模板

```yaml
rubric:
  problem_id: TPL-LINEAR-EQ-001
  full_score: 10
  step_weights:
    - step: 去括号
      weight: 2
      criteria: "分配律正确应用"
    - step: 移项
      weight: 2
      criteria: "符号变换正确"
    - step: 合并同类项
      weight: 2
      criteria: "同类项合并无误"
    - step: 系数化 1
      weight: 1
      criteria: "两边同时除以系数"
    - step: 验证
      weight: 1
      criteria: "代入原方程验证"
  result_weight: 1
  expression_requirements:
    - "写'解：'开头"
    - "写'x =' 而非'x:'"
    - "应用题带单位"
  deduction_rules:
    - "未写'解：'：-0.5"
    - "未验证：-0.5"
    - "单位错误：-1"
  misconception_flags:
    - "MIS-MATH-7-001"
    - "MIS-MATH-7-005"
```

## 语文题 Rubric 模板

```yaml
rubric:
  problem_id: TPL-READING-COMP
  full_score: 10
  dimensions:
    - name: 内容要点
      weight: 4
      criteria: "覆盖核心得分点"
    - name: 文本理解
      weight: 3
      criteria: "理解准确"
    - name: 表达
      weight: 2
      criteria: "通顺流畅"
    - name: 字数
      weight: 1
      criteria: "符合要求"
```

## 质量标准

- 权重总和 = 100
- 每个 step 有 criteria
- 配套 deduction_rules
- 关联到误区库
