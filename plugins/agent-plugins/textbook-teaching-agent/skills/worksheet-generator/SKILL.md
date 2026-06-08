---
name: worksheet-generator
description: 基于 curriculum_map 和学习目标，生成分层练习题（基础/中等/综合）、答案、解析、评分标准（rubric）。可对接教材原题或重写。
triggers:
  - /worksheet 命令
  - 教师说"出几道题"
  - lesson-planner 需要生成课堂练习
  - misconception-diagnoser 需要生成变式题
---

# Worksheet Generator Skill

## 用途

按"知识点 + 难度 + 数量"出题，输出 **题目 + 答案 + 解析 + 评分标准** 的完整练习。

输出必须能直接打印分发给学生，或直接录入 LMS。

## 触发场景

- `/worksheet <chapter> <difficulty> <count>`
- 教师备课需要课堂练习
- 学生错题补救需要变式题
- 单元复习需要综合卷

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| curriculum_map | ✅ | 知识图谱 |
| difficulty | ✅ | basic / medium / advanced / mixed |
| count | ✅ | 题目数量 |
| question_types | ❌ | 选择/填空/解答/应用题 |
| source | ❌ | textbook_only / textbook_derived / new |
| student_profile | ❌ | 影响难度和易错点 |
| include_rubric | ❌ | 默认 true |

## 输出

### `worksheet.md`（学生版，可隐藏答案）

```markdown
# 练习：正数和负数

> 教材：xxx
> 难度：基础 | 建议用时：20 分钟
> 姓名：_______ 班级：_______

## 一、选择题（每题 2 分，共 10 分）

1. 下列各数中，是负数的是（   ）
   A. -(-3)        B. |-2|
   C. -3²          D. 0

2. ...

## 二、填空题（每空 2 分，共 20 分）

1. 如果收入 100 元记作 +100 元，那么支出 50 元记作 _______ 元。
2. ...

## 三、解答题（每题 10 分，共 30 分）

1. 计算 |-5| + (-3) - 2
   ...

2. 某地白天温度 8°C，夜间 -3°C，温差是多少？
   ...
```

### `worksheet_answer.md`（教师/家长版）

```markdown
# 答案与解析：正数和负数

## 一、选择题
1. **C**  
   解析：-(-3)=3 是正数；|-2|=2 是正数；-3²=-9 是负数；0 既不是正数也不是负数。  
   教材依据：第 2 页正负数定义。

2. ...
```

### `rubric.md`（评分标准）

```markdown
# 评分标准

| 题号 | 满分 | 关键步骤分 | 表达分 | 备注 |
|---|---|---|---|---|
| 一.1 | 2 | 2 | 0 | 选择题只看结果 |
| 三.1 | 10 | 8 | 2 | 步骤：去绝对值 → 化符号 → 同号合并 → 异号相减 |
| 三.2 | 10 | 6 | 4 | 步骤：列式 → 计算 → 单位 |
```

## 工作流

```
输入参数
  ↓
1. 知识点筛选
   - 从 curriculum_map 选 3-5 个核心概念
   - 按难度分配：基础 60% + 中等 30% + 综合 10%（默认）
  ↓
2. 题源选择
   - 优先从 textbook_blocks 中检索相似原题（page_ref 标注）
   - 次选教材衍生题（修改数字或情境）
   - 末选原创题（标 source=new）
  ↓
3. 题型分配
   - 选择 / 填空 / 解答
   - 基础班少解答多选择填空
   - 拔高班多解答和应用题
  ↓
4. 题目生成
   - 每道题注明：题号 / 题型 / 分值 / 知识点 / 难度
   - 数学题确保计算结果可验证
   - 应用题确保情境真实可信
  ↓
5. 答案与解析
   - 选择/填空：直接给答案 + 1-2 句解析
   - 解答：分步骤给过程 + 关键步骤分
  ↓
6. Rubric
   - 步骤分：关键步骤占 70%
   - 结果分：最终结果占 20%
   - 表达分：单位/格式/术语占 10%
  ↓
7. 自检
   - 计算题必须自己算一遍
   - 应用题必须验证答案合理性
   - 检查是否覆盖所有指定知识点
   - 难度是否符合学生水平
  ↓
8. 导出
   - 学生版（可隐藏答案）
   - 教师版（含答案+解析）
   - DOCX / Markdown / PDF 多格式
```

## 实现要点

```python
def generate_worksheet(curriculum_map, difficulty, count, source, types):
    knowledge_points = select_kp(curriculum_map, count)  # 选知识点
    distribution = distribute_difficulty(difficulty, count)  # 难度分布
    
    questions = []
    for kp, diff in zip(knowledge_points, distribution):
        if source == 'textbook_only':
            q = retrieve_textbook_question(kp, diff, types)
        elif source == 'textbook_derived':
            q = derive_question(kp, diff, types)
        else:
            q = compose_question(kp, diff, types)
        q.page_ref = q.get('page_ref')  # 教材来源
        questions.append(q)
    
    answers = compute_answers(questions)
    rubric = build_rubric(questions)
    return Worksheet(questions, answers, rubric)
```

## 质量标准

| 维度 | 标准 |
|---|---|
| 知识点覆盖 | ≥ 95% 核心概念 |
| 难度匹配 | 实际难度与标注难度一致率 ≥ 85% |
| 答案正确率 | 100%（必须自检） |
| Rubric 可执行 | 教师可直接按表给分 |
| 教材引用 | textbook_only 模式 100% 有 page_ref |
| 变式区分度 | 变式题与原题可识别为"同类不同形" |

## 与其他 skill 的关系

- **上游**：`curriculum-mapper`（知识点）、`math-example-generator`（数学出题模板）
- **下游**：`feedback-writer`（包装输出）、`homework-reviewer`（批改对接）

## 护栏

1. **不超纲**：题目不能超出学生年级和教材范围
2. **不重复**：每道题独立，不与之前的练习重复
3. **不超量**：题目数量、难度、总分符合输入约束
4. **答案可验**：每道题教师能自己算一遍验证
5. **应用题真实**：情境真实可计算，避免"1 只鸡 + 1 只鸭 = 2 只鸡鸭"
6. **不替学生作弊**：题目、答案、解析分离存储，分发时可隐藏答案

## 不要做的事

- 不要替学生做完整解题（解析是给教师/家长看的，学生版可隐藏）
- 不要出刁钻偏题（偏离教材原意）
- 不要混入广告或无关内容
- 不要给"送分题"凑数（每道题都有诊断价值）
