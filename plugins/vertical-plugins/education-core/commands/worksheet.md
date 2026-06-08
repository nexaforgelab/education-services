---
name: worksheet
description: 生成分层练习题、答案、解析、评分标准。
usage: /worksheet <chapter> <difficulty> <count>
---

# /worksheet 命令

按"知识点 + 难度 + 数量"出题。

## 语法

```
/worksheet <chapter> <difficulty> <count>
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| chapter | ✅ | 章节名 / 章节 ID |
| difficulty | ✅ | basic / medium / advanced / mixed |
| count | ✅ | 题目数量 |

## 行为

调用 `worksheet-generator` skill 和学科垂直 skill（如 `math-example-generator`）：

1. 选知识点（3-5 个）
2. 按难度分布
3. 选题型（选择/填空/解答/应用题）
4. 优先教材原题 / 衍生 / 原创
5. 写答案 + 解析 + 评分标准

## 输出

```
out/worksheet/
├── worksheet_student.md     # 学生版（可隐藏答案）
├── worksheet_teacher.md      # 教师版（答案+解析）
├── rubric.md                 # 评分标准
├── variations.md             # 变式题
└── source_mapping.md         # 题目来源（教材页码）
```

## 难度分布（默认）

- mixed: 基础 60% + 中等 30% + 综合 10%
- basic: 基础 100%
- medium: 中等 100%
- advanced: 综合 100%

## 题源策略

1. 优先教材原题（标 page_ref）
2. 次选教材衍生（改数字或情境）
3. 末选原创（标 source=new）

## 质量保证

- 答案正确率 100%（自检）
- 知识点覆盖 ≥ 95%
- 难度匹配 ≥ 85%
- Rubric 可直接给分

## 示例

```
/worksheet 有理数加减法 mixed 10
/worksheet 一元一次方程 basic 15
```

## 边界

- 不超纲
- 不重复
- 不出偏题
- 不替学生做题
