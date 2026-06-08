---
name: diagnose-homework
description: 诊断学生错题，输出错因、补救讲解、变式题。
usage: /diagnose-homework <homework_file> <chapter>
---

# /diagnose-homework 命令

把学生作业的错题变成可执行的补救方案。

## 语法

```
/diagnose-homework <homework_file> <chapter>
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| homework_file | ✅ | 作业图片 / PDF / 文字文件路径 |
| chapter | ✅ | 对应章节 |

## 行为

调用 `homework-reviewer` skill 和 `misconception-diagnoser` skill：

1. OCR / 文本提取
2. 题目-答案对齐
3. 错因分类（概念/计算/审题/方法/步骤/表达/前置/迁移）
4. 错题讲解（教师版/家长版）
5. 变式题（基础→中等→综合）
6. 复习建议

## 输出

```
out/diagnosis/
├── report_teacher.md        # 教师版报告
├── report_parent.md         # 家长版报告
├── diagnosis.json           # 结构化诊断
├── error_analysis.md        # 错因分析
├── explanations.md          # 错题讲解
├── variation_problems.md    # 变式题
└── review_plan.md           # 复习计划
```

## 错因分类

- concept_error: 概念错
- calculation_error: 计算错
- careless_error: 审题/抄写错
- method_error: 方法错
- step_missing: 步骤缺失
- expression_error: 表达不规范
- prerequisite_gap: 前置知识缺失
- transfer_error: 类比迁移错

## 质量保证

- 批改准确率 ≥ 98%
- 错因诊断准确率 ≥ 80%
- 学生评语具体到步骤
- 家长讲解口语化可执行
- 变式题难度递进

## 示例

```
/diagnose-homework ./samples/homework_001.jpg ch01_s05
```

## 边界

- 不羞辱学生
- 不空泛评语
- 不替学生答题
- 不自动推送给学生
