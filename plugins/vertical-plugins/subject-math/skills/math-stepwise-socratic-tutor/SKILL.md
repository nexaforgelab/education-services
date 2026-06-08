---
name: math-stepwise-socratic-tutor
description: 用苏格拉底式提问引导学生思考数学问题，不直接给答案，按"已知/未知/方法/计算/反思"五步递进提问。
triggers:
  - 学生在 Agent 引导下做题
  - 错题诊断后的补救讲解（学生版）
  - 教师希望培养学生的解题思维
---

# Math Stepwise Socratic Tutor Skill

## 用途

不直接给答案，而是 **用 5 个递进问题** 引导学生自己走到答案。

面向学生：**思维比答案重要**。
面向教师/家长：可以参考这个流程辅助学生。

## 5 步提问法

```
Step 1: 已知什么？   → 引导学生读题、提取条件
Step 2: 求什么？     → 明确目标
Step 3: 学过什么方法？→ 联想章节知识点
Step 4: 怎么用？     → 把方法应用到本题
Step 5: 对吗？       → 验证答案合理性
```

## 触发场景

- 学生做题卡住
- 学生问"这题怎么做"
- 错题补救的学生版讲解
- 单元复习中的"思维训练"

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| problem | ✅ | 题目 |
| student_answer | ❌ | 学生当前答案（若有） |
| grade | ✅ | 年级 |
| stuck_step | ❌ | 学生卡在哪步（1-5） |

## 输出

```json
{
  "problem": "计算 (-3) + 5 - (-2)",
  "tutor_script": [
    {
      "step": 1,
      "question": "题目中给了哪些数？",
      "purpose": "提取条件",
      "expected_response": "-3, 5, -2",
      "hint_if_no_response": "看看每个数字前面的符号"
    },
    {
      "step": 2,
      "question": "我们要求什么？",
      "purpose": "明确目标",
      "expected_response": "三个数的和"
    },
    {
      "step": 3,
      "question": "我们学过哪些方法处理减法？",
      "purpose": "联想章节知识点",
      "expected_response": "减法 = 加相反数",
      "page_ref": "教材 p.18"
    },
    {
      "step": 4,
      "question": "那 -(-2) 是什么？先把它变出来",
      "purpose": "应用方法",
      "expected_response": "2"
    },
    {
      "step": 5,
      "question": "现在原式变成什么？加起来",
      "purpose": "计算",
      "expected_response": "-3 + 5 + 2 = 4"
    }
  ],
  "validation": {
    "question": "这个结果合理吗？用什么方法再验一遍？",
    "expected_response": "用相反顺序：5 + 2 - 3 = 4 ✓"
  },
  "meta": {
    "estimated_minutes": 5,
    "encouragement": "你已经会减法化加法了！"
  }
}
```

## 工作流

```
输入题目
  ↓
1. 题目解析
   - 提取条件
   - 明确目标
   - 识别考点
  ↓
2. 设计 5 步问题
   - 步 1: 已知什么
   - 步 2: 求什么
   - 步 3: 学过什么方法
   - 步 4: 怎么用
   - 步 5: 验证
  ↓
3. 兜底提示
   - 学生答不上 → 给更具体的提示
   - 学生答错 → 引导反思
   - 学生答对 → 继续下一步
  ↓
4. 总结
   - 验证
   - 鼓励
   - 关联到章节
```

## 实现要点

```python
def socratic_tutor(problem, grade, stuck_step=None):
    parsed = parse_problem(problem)
    questions = design_5_questions(parsed)
    if stuck_step:
        questions = questions[stuck_step-1:]  # 从卡住那步开始
    return TutorScript(questions)
```

## 质量标准

- 5 步问题必须递进
- 每步问题明确具体（不空泛）
- 兜底提示必须有
- 验证步骤必须有
- 鼓励必须具体

## 兜底提示原则

| 学生状态 | 处理 |
|---|---|
| 完全没思路 | 退到步 1，给更具体的提示 |
| 答错 | 不直接纠错，问"你能再读一遍题吗" |
| 部分对 | "这部分对了，那剩下的呢" |
| 全对 | 继续下一步 + 鼓励 |

## 护栏

1. **不直接给答案**：必须让学生自己走到
2. **不羞辱**：答错时说"我们再看看"，不说"又错了"
3. **不超纲**：问题不超过学生年级
4. **不堆问题**：5 步左右，不超过 7 步
5. **耐心**：给时间想，不催促

## 不要做的事

- 不要在 5 步问题中夹带答案
- 不要写"答案是 X，因为 ..."
- 不要给学生 10 步问题
- 不要用苏格拉底式讲题法但跳过验证
