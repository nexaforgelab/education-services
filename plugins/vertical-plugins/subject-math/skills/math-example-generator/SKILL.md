---
name: math-example-generator
description: 数学专属出题器：基于知识点 + 难度生成例题、变式题、应用题。维护题模板、参数化生成、答案可验。
triggers:
  - worksheet-generator 需要数学题
  - misconception-diagnoser 需要变式题
  - 教师需要课堂例题
---

# Math Example Generator Skill

## 用途

为数学学科提供 **高质量、可参数化、答案可验证** 的出题能力。

## 题模板示例

```yaml
- template_id: TPL-RAT-ADD-SAME
  concept: 同号有理数相加
  difficulty: basic
  template: "({a}) + ({b}) = ?"
  generator: |
    a = random.choice(range(-20, 0))
    b = random.choice(range(-20, 0))
    answer = a + b
  variations:
    - template: "({a}) + ({b}) = ?"
    - template: "计算 ({a}) + ({b}) 的值"
  pre_requisites: [kp_positive, kp_negative]
  page_refs: [ch01_s05_p15]

- template_id: TPL-RAT-ADD-DIFF
  concept: 异号有理数相加
  difficulty: basic
  template: "({a}) + ({b}) = ?"
  generator: |
    sign1 = random.choice([-1, 1])
    sign2 = -sign1
    abs1 = random.randint(1, 20)
    abs2 = random.randint(1, 20)
    a, b = sign1*abs1, sign2*abs2
    answer = a + b
  pre_requisites: [kp_positive, kp_negative, kp_absolute_value]
  common_misconception: MIS-MATH-7-001

- template_id: TPL-LINEAR-EQ
  concept: 一元一次方程
  difficulty: medium
  template: "{a}x + {b} = {c}"
  generator: |
    x = random.randint(-10, 10)
    a = random.choice([2,3,4,5])
    b = random.randint(-10, 10)
    c = a*x + b
  answer_x: x
  pre_requisites: [kp_linear_equation_basics]
```

## 工作流

```
输入 (知识点 + 难度 + 数量)
  ↓
1. 选模板
   - 从模板库筛匹配的模板
   - 按难度过滤
  ↓
2. 参数化生成
   - 每模板运行 generator
   - 检查答案合理性
  ↓
3. 验证
   - 答案必须数学正确
   - 题目不能退化（如 0+0）
   - 难度与标注一致
  ↓
4. 包装输出
   - 题目 + 答案 + 解析
   - 关联 page_ref
  ↓
5. 多样性检查
   - 不与已有题目重复
   - 数字/情境有差异
```

## 实现要点

```python
def generate_math_problems(concept, difficulty, count, blocks=None):
    templates = load_templates(concept=concept, difficulty=difficulty)
    problems = []
    while len(problems) < count:
        tpl = random.choice(templates)
        prob = instantiate(tpl)
        if validate(prob) and not duplicate(prob, problems):
            problems.append(prob)
    return problems

def validate(problem):
    # 1. 数学正确
    if not check_math(problem):
        return False
    # 2. 答案非平凡
    if problem.answer in [0, 1, -1] and not problem.allow_trivial:
        return False
    # 3. 难度匹配
    if not matches_difficulty(problem, problem.declared_difficulty):
        return False
    return True
```

## 质量标准

- 答案正确率 100%（自检）
- 难度匹配 ≥ 85%
- 模板覆盖 ≥ 90% 核心知识点
- 参数化无重复
- 包含 page_ref

## 难度定义

| 难度 | 数字范围 | 步骤数 | 概念数 |
|---|---|---|---|
| basic | 1-20 | 1-2 | 1 |
| medium | 1-100 | 2-4 | 1-2 |
| advanced | 1-1000 | 4+ | 2-3 |

## 应用题模板

应用题需要更多结构化：

```yaml
- template_id: TPL-WP-MIXTURE
  concept: 浓度问题
  difficulty: medium
  template: "现有 {a}% 的盐水 {b} 克，加入 {c} 克水，新浓度是？"
  generator: |
    a = random.randint(5, 30)
    b = random.randint(100, 500)
    c = random.randint(50, 200)
    new_concentration = round(a * b / (b + c), 2)
  context_requirements:
    - 数字必须真实可信
    - 步骤必须清晰
    - 单位必须明确
```

## 护栏

1. **数学正确**：自检 + 必要时调用 sympy 验证
2. **不超纲**：数字范围、概念数符合年级
3. **应用题真实**：情境必须可信
4. **不堆题海**：每题都有诊断价值
5. **不重复**：每次生成都不与上次重复

## 不要做的事

- 不要在题目中夹带"教学指令"（如"请仔细审题"）
- 不要给诱导性题目（答案藏在题目里）
- 不要在答案中夹带"重要提示"（让答案就是答案）
- 不要给"陷阱题"（不健康）
