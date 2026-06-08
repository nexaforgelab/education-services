---
name: math-word-problem-builder
description: 应用题专属构建器：基于真实生活情境、参数化生成、条件自洽、可解、有教育意义。覆盖行程/工程/利润/浓度/比例/几何等典型应用题。
triggers:
  - worksheet-generator 需要应用题
  - 教师需要生活化例题
  - 单元复习需要综合应用题
---

# Math Word Problem Builder Skill

## 用途

构建 **真实情境 + 条件自洽 + 难度可控 + 答案可验** 的数学应用题。

应用题的最大问题是"假、大、空"，本 skill 严格把控。

## 题目结构

```yaml
problem:
  context:
    scenario: 真实情境
    characters: 角色
    objects: 物品
  question:
    known:
      - 条件 1
      - 条件 2
    unknown: 求什么
  numbers:
    - 数字 1
    - 数字 2
  solution:
    steps:
      - 步骤 1
      - 步骤 2
    answer: X
    unit: 元 / 米 / 千克
  meta:
    chapter: 一元一次方程
    concepts: [kp_linear_equation, kp_word_problem_translation]
    difficulty: medium
    page_ref: ch04_s02_p78
```

## 工作流

```
输入 (知识点 + 难度 + 情境)
  ↓
1. 选情境
   - 从情境库筛
   - 按年级适配
  ↓
2. 选数学结构
   - 行程 / 工程 / 利润 / 浓度 / 比例 / 几何
   - 对应方程类型
  ↓
3. 反向构造
   - 先设答案
   - 反推条件
   - 检查条件自洽
  ↓
4. 正向表达
   - 把数字、情境写为题目
   - 标"已知"和"求"
  ↓
5. 验证
   - 答案正确
   - 数字合理
   - 条件无矛盾
   - 难度匹配
  ↓
6. 多样性检查
   - 不与已有题重复
   - 情境有差异
```

## 典型应用题类型

### 1. 行程问题

```yaml
context: 小明从家走到学校
template: "{A} 从甲地出发，速度 {v1} m/s；{B} 从乙地出发，速度 {v2} m/s。两地相距 {d} m。问几秒后两人相遇？
generator: |
  v1 = random.randint(2, 8)
  v2 = random.randint(2, 8)
  d = random.randint(100, 1000)
  t = d / (v1 + v2)
  # 注意：t 最好为整数
```

### 2. 工程问题

```yaml
context: 修路/挖水渠/刷墙
template: "甲单独做 {a} 天完成，乙单独做 {b} 天完成。甲乙合做几天完成？
generator: |
  a = random.randint(5, 20)
  b = random.randint(5, 20)
  # 验证答案不是整数时调整
  while (a*b) % (a+b) != 0:
    a, b = random.randint(5,20), random.randint(5,20)
```

### 3. 利润问题

```yaml
context: 商店定价
template: "某商品进价 {c} 元，按 {p}% 的利润率定价，售价多少？
generator: |
  c = random.randint(50, 500)
  p = random.choice([20, 30, 40, 50])
  price = c * (1 + p/100)
```

### 4. 浓度问题

```yaml
context: 盐水/糖水
template: "{a}% 的盐水 {b} 克，加入 {c} 克水，新浓度是？
generator: |
  a = random.randint(5, 30)
  b = random.randint(100, 500)
  c = random.randint(50, 200)
```

### 5. 比例问题

```yaml
context: 分配/配料
template: "甲、乙、丙按比例 {a}:{b}:{c} 分配 {d} 千克。各分多少？
```

### 6. 几何应用

```yaml
context: 矩形/三角形/圆
template: "长方形长 {a} 宽 {b}，面积是？
```

## 实现要点

```python
def build_word_problem(chapter, difficulty, scenario=None):
    template = select_template(chapter, difficulty, scenario)
    problem = instantiate(template)
    problem = reverse_engineer_check(problem)  # 反向验证
    if not is_valid(problem):
        return build_word_problem(chapter, difficulty, scenario)  # 重试
    return problem

def is_valid(problem):
    return (
        has_realistic_context(problem) and
        has_consistent_conditions(problem) and
        has_correct_answer(problem) and
        matches_difficulty(problem) and
        not duplicates_existing(problem)
    )
```

## 质量标准

- 情境真实可信（数字、角色、地点都对得上）
- 条件自洽（无矛盾，无多余条件）
- 答案正确（数学验证）
- 难度匹配年级
- 数字合理（不出现 1234.56 这种）
- 单位明确

## 护栏

1. **真实情境**：不写"小明有 99999999 元"这种离谱
2. **条件自洽**：不能给"小李 5 分钟走 100 公里"这种
3. **答案合理**：解方程结果不能是负数（除非特别说明）
4. **无多余条件**：不要塞入不参与计算的"烟雾弹"
5. **无歧视**：避免涉及性别、地域、收入歧视的情境
6. **不夹带指令**：不在题目中写"请仔细审题"、"注意 ..."

## 不要做的事

- 不要在应用题中夹带价值观判断
- 不要写"某人因为不努力而失败"
- 不要给"陷阱题"或"脑筋急转弯"
- 不要把"鸡兔同笼"等老题原样照搬（可改编）
- 不要超出年级认知（小学低年级不要"年利率"问题）

## 反面示例

❌ "一家商店卖衣服，每件成本 50 元，老板想要赚 100%，那么定价是多少？"
   - "100% 利润"对低年级抽象

❌ "小明今年 5 岁，爸爸 35 岁，几年后爸爸的年龄是小明的 5 倍？"
   - 答案要验证合理性

❌ "一批零件，甲单独做 7 天完成，乙单独做 9 天完成，丙单独做 12 天完成，三人合做 3 天能否完成？"
   - 答案要算完再写题目，避免"是"或"否"模糊

## 正面示例

✅ "某商品每件进价 80 元，按 25% 的利润率定价，售价多少元？"
   - 情境真实，答案简单

✅ "一项工程，甲队单独做需要 12 天，乙队单独做需要 18 天。两队合做，多少天可以完成？"
   - 条件自洽，答案 7.2 天也合理

✅ "小明从家到学校 1200 米，他每分钟走 80 米。走到一半时想起忘带作业本，回家取了再走。问小明到学校一共走了多少米？"
   - 条件略多但都参与计算，有趣
