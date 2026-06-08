---
name: math-concept-explainer
description: 把数学概念拆成三层解释：直观（生活类比）、符号（数学语言）、应用（教材例题）。为教师、家长、学生三角色提供不同版本。
triggers:
  - 教师备课需要解释概念
  - 家长需要给孩子讲懂
  - Agent 输出教师版 / 家长版讲解
---

# Math Concept Explainer Skill

## 用途

数学概念的"翻译机"——把抽象数学翻译成：

- **直观版**：生活类比、图像化（面向家长 / 基础薄弱学生）
- **符号版**：严格数学定义、形式化（面向教师 / 拔高学生）
- **应用版**：教材例题 + 变式（面向所有人）

## 触发场景

- `/lesson-plan` 中需要"概念讲解"部分
- `/explain-to-parent` 中需要家长能懂的概念解释
- `unit-review-agent` 中需要概念梳理
- 错题诊断中需要"概念回顾"

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| concept | ✅ | 概念名（如"负数"、"一元一次方程"） |
| grade | ✅ | 年级 |
| audience | ✅ | teacher / parent / student |
| textbook_blocks | ❌ | 教材原文 |
| depth | ❌ | shallow / standard / deep |

## 输出

### 1. 直观版（家长/学生）

```
【生活类比】
- 负数 = 欠条。收入 100 元 = +100，借出 50 元 = -50。
- 数轴 = 楼梯。0 楼，往上正数，往下负数。
- 异号相加 = 两个人往相反方向走，谁走得远听谁的。

【图像化】
- 用温度计 / 海拔图 / 收支表 演示
- 用数轴标点

【口诀】（如适用）
- 同号相加取同号，绝对值相加
- 异号相加取大号，绝对值相减
- 减法统一变加法
```

### 2. 符号版（教师/拔高）

```
【形式化定义】
设 a, b ∈ ℚ，则
- 同号相加：a + b = (|a| + |b|) × sign(a)  （a,b 同号）
- 异号相加：a + b = (||a| - |b||) × sign(较大绝对值)
- 减法：a - b = a + (-b)

【性质】
- 交换律：a + b = b + a
- 结合律：(a + b) + c = a + (b + c)
- 0 是加法单位元：a + 0 = a
- 相反数：a + (-a) = 0

【关键证明】（如适用）
- 减法即加相反数：a - b = a + (-b)
  证明：设 c = a - b，则 c + b = a，故 c = a + (-b)
```

### 3. 应用版

```
【教材例题】
- 例 1（教材 p.X）：计算 (-3) + 5
  步骤：1) 异号 2) 绝对值 5 > 3 3) 结果 + (5-3) = +2
  
【变式题】
- 基础：3 + (-5) = ?
- 中等：(-3) + (-5) = ?
- 综合：|-3| + 5 - 2 = ?

【易错提醒】
- 把"减负数"和"减一个负数"混淆
- 计算绝对值时忘记符号
```

## 工作流

```
输入 concept
  ↓
1. 概念识别
   - 是定义？性质？定理？公式？
   - 关联哪些前置知识？
  ↓
2. 拉教材
   - 概念定义原文（页码）
   - 例题和变式
  ↓
3. 类比构建（直观版）
   - 找 1-2 个生活类比
   - 用图像化辅助
   ↓
4. 形式化（符号版）
   - 数学语言定义
   - 关键性质
   - 证明思路（深度 deep 时）
  ↓
5. 例题（应用版）
   - 教材原题
   - 难度递进变式
   - 易错提醒
  ↓
6. 按 audience 调整
   - teacher: 三版都给
   - parent: 只给直观版
   - student: 直观版 + 应用版
```

## 实现要点

```python
def explain_concept(concept, grade, audience, blocks):
    definition = extract_definition(blocks)  # 教材定义
    analogy = build_analogy(concept)         # 生活类比
    formal = build_formal(concept)            # 符号化
    examples = build_examples(concept, blocks) # 教材例题
    variations = build_variations(concept)     # 变式
    pitfalls = load_pitfalls(concept)          # 易错
    
    if audience == 'parent':
        return render(analogy, examples, pitfalls)  # 只要直观+例题
    elif audience == 'student':
        return render(analogy, examples, variations)
    else:  # teacher
        return render(definition, formal, analogy, examples, variations, pitfalls)
```

## 质量标准

- 类比必须真实可类比（不要"负数像欠条，但本质不是债"）
- 符号化必须严格（不要"差不多就行"）
- 例题 100% 引用教材页码
- 变式难度递进
- 易错点具体到操作步骤

## 护栏

1. **类比不能"硬凑"**：如果找不到好类比，就不勉强
2. **不编造定义**：必须基于教材 + 课标
3. **不混淆概念**：注意"负数" vs "小于 0 的数"（虽然等价）
4. **不堆砌公式**：能直观就别上公式
5. **不教条**：低年级不要过早引入形式化定义

## 不要做的事

- 不要给出"概念的发展史"（除非用户问）
- 不要给"哲学层面的思考"（这是科普，不是辅导）
- 不要给"考试分值占比"（让教师自己判断）
- 不要给学生写"你应该记住 ..."的口吻
