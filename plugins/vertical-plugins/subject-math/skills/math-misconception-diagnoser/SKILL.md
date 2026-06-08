---
name: math-misconception-diagnoser
description: 数学专属误区库与诊断：符号/单位/运算顺序/等量关系/几何直观/坐标/函数/方程等常见误区的识别与补救。
triggers:
  - 数学作业错因诊断
  - 数学单元复习
  - 教师提问"这个错误为什么总犯"
---

# Math Misconception Diagnoser Skill

## 用途

沉淀数学学科的 **误区库**，并提供识别 + 补救的标准化方法。

## 误区库结构

```yaml
# misconceptions.yaml
- id: MIS-MATH-7-001
  grade: 7
  chapter: 有理数
  concept: 有理数加减法
  misconception: 减负数时未变号
  detection_pattern:
    - (-a) - (-b) → student writes -a - b
    - 7 - (-3) → student writes 7 - 3 = 4
  typical_problem: "(-3) - (-5) = -8"
  correct_approach: "(-3) - (-5) = -3 + 5 = 2"
  remediation:
    analogy: "减一个负数 = 把债收回 = 加正数"
    socratic_questions:
      - "看到 '减负数'，第一步要做什么？"
      - "-(-2) 等于什么？"
    practice:
      - "(-5) + 3 - (-4) = ?"
      - "7 - (-3) + (-5) = ?"
  page_refs: [ch01_s05_p18]
  severity: high
```

## 数学典型误区（按章节）

### 七年级

| 章节 | 误区 | 学生表现 | 补救 |
|---|---|---|---|
| 有理数 | 减负数未变号 | 7-(-3)=4 | 反复练减法化加法 |
| 有理数 | 异号相加取错符号 | (-3)+5=-2 | 数轴演示 |
| 整式 | 漏乘分配律 | 2(x+3)=2x+3 | 强调"每一项都乘" |
| 整式 | 同类项合并错 | 3x+2y=5xy | 强化"字母和指数都相同" |
| 一元一次方程 | 移项不变号 | 3x=6 → x=2 对，但 x+3=5 → x=2 | 强调"过桥变号" |
| 一元一次方程 | 去分母漏乘 | x/2 + 1 = 3 → x+1=3 | 每项都乘 |
| 几何 | 混淆角和线 | "直线 AB" 和 "线段 AB" | 强调定义 |

### 八年级

| 章节 | 误区 | 学生表现 | 补救 |
|---|---|---|---|
| 三角形 | 边角对应错 | 错把"对边" 当 "邻边" | 画图标注 |
| 全等三角形 | 错用 SSA | 已知两边一锐角 | 强调判定定理 |
| 一次函数 | 斜率 k 和截距 b 弄反 | y=kx+b 当 y=x+b | 多练 |
| 整式乘法 | 完全平方记错 | (a+b)² = a²+b² | 反复练 |

### 九年级

| 章节 | 误区 | 学生表现 | 补救 |
|---|---|---|---|
| 一元二次方程 | 漏解 | 求根公式只算 1 个根 | 强调 ± |
| 二次函数 | 顶点坐标记反 | (-b/2a, c) 还是 (-b/2a, (4ac-b²)/4a) | 多次练 |
| 相似三角形 | 比例对应错 | 对应边比例找错 | 画图标注 |

## 工作流

```
错题 + 学生答案
  ↓
1. 题目解析
   - 提取考点
   - 识别正确解法
  ↓
2. 误区匹配
   - 比对误区库 detection_pattern
   - 计算匹配分
  ↓
3. 误区命中
   - 命中已知 → 复用解释模板
   - 未命中 → 通用分析
  ↓
4. 严重度评估
   - high: 核心概念错
   - medium: 单点错
   - low: 粗心
  ↓
5. 补救方案
   - 类比
   - 苏格拉底问题
   - 变式练习
```

## 实现要点

```python
def diagnose_math_error(problem, student_answer, correct_answer, grade):
    parsed = parse_math_problem(problem)
    error_type = classify_error(student_answer, correct_answer)
    
    # 查误区库
    matches = search_misconceptions(
        grade=grade,
        chapter=parsed.chapter,
        pattern=parsed.pattern
    )
    
    if matches:
        misconception = matches[0]
        return MisconceptionResult(
            matched=True,
            misconception=misconception,
            remediation=misconception.remediation
        )
    else:
        return MisconceptionResult(
            matched=False,
            error_type=error_type,
            remediation=build_generic_remediation(error_type)
        )
```

## 质量标准

- 误区库条目 ≥ 100（每个年级 30+）
- 识别准确率 ≥ 80%
- 补救方案可执行

## 护栏

1. **不夸大误区**：常见错误不一定是"误区"，可能是粗心
2. **不忽略情境**：同一个错在不同题目可能是不同原因
3. **不羞辱**：写"误区"是教学术语，不是"学生笨"
4. **可解释**：每条误区必须有 detection_pattern 可验证

## 与其他 skill 的关系

- **上游**：`textbook-ingestion`（提供题目）
- **调用**：`misconception-diagnoser`（通用错因）
- **下游**：`math-rubric-grader`（批改）、`worksheet-generator`（变式题）

## 维护

误区库按月更新：

- 从作业诊断中提取新误区
- 教师反馈校正
- 学期结束时复盘
