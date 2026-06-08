---
name: math-rubric-grader
description: 数学专属批改器：按步骤给分（过程分），识别关键步骤、关键概念引用、表达规范性。区分概念错/计算错/步骤缺失/表达不规范。
triggers:
  - homework-reviewer 需要数学批改
  - 教师需要标准化的步骤分
---

# Math Rubric Grader Skill

## 用途

数学题的"步骤分"批改——比单纯判断对错更精细，按"过程"和"表达"分别给分。

## 评分维度

```
总分 = 步骤分 (70%) + 结果分 (20%) + 表达分 (10%)
```

| 维度 | 占比 | 说明 |
|---|---|---|
| 步骤分 | 70% | 关键步骤的完整性和正确性 |
| 结果分 | 20% | 最终答案正确性 |
| 表达分 | 10% | 单位、格式、术语 |

## 步骤分类

| 步骤类型 | 权重 | 说明 |
|---|---|---|
| 概念引用 | 高 | 明确写出"根据 X 定理" |
| 关键变换 | 高 | 符号变换、合并、化简 |
| 计算 | 中 | 实际数字运算 |
| 验证 | 中 | 代入验证、特值验证 |
| 表达 | 低 | 单位、格式 |

## 工作流

```
题目 + 学生解答
  ↓
1. 题目解析
   - 识别考点
   - 列预期步骤（基于标准解法）
  ↓
2. 学生解答分步
   - 拆为原子步骤
   - 标注每个步骤的目的
  ↓
3. 步骤比对
   - 学生步骤 vs 标准步骤
   - 缺失步骤 → 扣分
   - 错误步骤 → 扣分
   - 多余步骤 → 不扣分
  ↓
4. 错因分类
   - 概念错 / 计算错 / 步骤缺失 / 表达不规范
  ↓
5. 分数计算
   - 步骤分 + 结果分 + 表达分
  ↓
6. 反馈
   - 具体到步骤的批注
   - 改进建议
```

## 示例

```
题目：解方程 2(x+3) = 4x - 6
满分：10 分

标准步骤：
S1. 去括号：2x + 6 = 4x - 6
S2. 移项：2x - 4x = -6 - 6
S3. 合并：-2x = -12
S4. 系数化 1：x = 6
S5. 验证（可选）：2(6+3) = 18; 4×6-6 = 18 ✓

学生解答：
S1. 2x + 6 = 4x - 6              ✓ (步骤分 2/2)
S2. 2x = 4x - 6 - 6              ✗ 移项未变号（扣 1 分，1/2）
S3. -2x = -12                    ✗ 由 S2 错导致，但本身正确（不重扣 0/0）
S4. x = 6                        ✗ 应为 x=6（学生写 -6）

分数：
- 步骤分：2+1+0+0 = 3/8
- 结果分：-6 错（0/1）
- 表达分：未写"解：" -0.5；未验证 -0.5
- 总分：3 + 0 + 0.5 = 3.5 / 10

批注：
"S1 正确。S2 移项时没变号：4x 移到左边应变为 -4x，-6 移到左边应变为 +6。  
建议：移项时强调"过桥变号"。S4 答案错误由 S2 传递。"
```

## 实现要点

```python
def grade_math(problem, student_solution, rubric):
    standard_steps = decompose(rubric.standard_solution)
    student_steps = decompose(student_solution)
    
    matches = align_steps(standard_steps, student_steps)
    step_score = compute_step_score(matches, rubric.step_weights)
    result_score = check_result(student_solution, rubric.correct_answer)
    expression_score = check_expression(student_solution, rubric.expression_requirements)
    
    error_type = classify_error(matches)
    return GradeResult(
        step_score=step_score,
        result_score=result_score,
        expression_score=expression_score,
        total=step_score + result_score + expression_score,
        error_type=error_type,
        comments=generate_comments(matches, error_type)
    )
```

## 质量标准

- 步骤比对准确率 ≥ 95%
- 错因分类准确率 ≥ 80%
- 批注具体到步骤
- 分数合理（不与教师手改有 >1 分差距）

## 护栏

1. **不只判对错**：必须给步骤分
2. **不只算结果**：学生写对结果但过程错的不能满分
3. **不忽略过程**：学生写对过程但结果错的酌情给分
4. **不羞辱**：批注要建设性
5. **不一刀切**：根据 rubric 而非统一标准

## 与其他 skill 关系

- **调用**：`math-misconception-diagnoser`（错因）
- **被调用**：`homework-reviewer`（批改）
- **配合**：`worksheet-generator`（rubric 输出）

## Rubric 模板

```yaml
rubric:
  problem_id: TPL-LINEAR-EQ-001
  full_score: 10
  step_weights:
    - step: 去括号
      weight: 2
    - step: 移项
      weight: 2
    - step: 合并同类项
      weight: 2
    - step: 系数化 1
      weight: 1
    - step: 验证
      weight: 1
  result_weight: 1
  expression_requirements:
    - 写"解："
    - 写"x ="
    - 单位（如果应用题）
  deduction_rules:
    - "未写'解：'：-0.5"
    - "未验证：-0.5"
```
