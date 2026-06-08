---
name: homework-reviewer
description: 批改学生提交的作业，对接 misconception-diagnoser，输出批改结果（对/错/部分对）、错因、补救讲解、变式题；为教师/家长提供"看完就能用"的作业分析报告。
triggers:
  - /diagnose-homework 命令
  - homework-diagnosis-agent 调用的核心 skill
  - 教师提交学生作业请求批改
---

# Homework Reviewer Skill

## 用途

把"批改作业"做成 **结构化、有诊断价值、可执行的产出**，而不是简单的对错标记。

对教师：节省 80% 批改时间，同时拿到错因统计、班级薄弱知识点报告。
对家长：拿到一份"孩子卡在哪里、怎么补"的清单。

## 触发场景

- 学生提交作业图片 / 文字答案
- 教师上传班级作业
- 家长上传孩子作业
- `/diagnose-homework <homework> <chapter>`

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| homework | ✅ | 题目 + 学生答案（文字或 OCR 后） |
| chapter_id | ✅ | 对应章节 |
| student_profile | ❌ | 影响错因历史和变式题难度 |
| class_id | ❌ | 若为班级作业，可统计班级薄弱点 |
| standard_answer | ❌ | 缺失时由 Agent 自行从教材生成 |
| output_format | ❌ | teacher_report / parent_report / both |

## 输出

### 1. 批改结果（per-question）

```json
{
  "question_id": "q03",
  "question_text": "...",
  "student_answer": "...",
  "correct_answer": "...",
  "result": "partial",  // correct | wrong | partial | uncertain
  "score": 6,           // 满分 10
  "error_type": "calculation_error",
  "knowledge_points": ["有理数加减法"],
  "comment_for_student": "符号处理对了，最后一步 5-1=4 写成 5-1=5，建议重算",
  "comment_for_teacher": "q03 全班 60% 错在最后一步，可能是抄写或心算"
}
```

### 2. 整体报告

```markdown
# 作业分析报告

> 学生：xxx | 班级：七年级 X 班
> 作业：《xxx》第 X 课时练习
> 提交时间：2026-06-07
> 批改时间：2026-06-07

## 一、整体情况

| 维度 | 数据 |
|---|---|
| 总题数 | 10 |
| 正确 | 6 |
| 错误 | 3 |
| 部分对 | 1 |
| 正确率 | 60% |
| 用时估计 | 25 分钟 |

## 二、错因分布

| 错因类型 | 数量 | 占比 |
|---|---|---|
| 概念错 | 1 | 25% |
| 计算错 | 2 | 50% |
| 步骤缺失 | 1 | 25% |

## 三、薄弱知识点 TOP 3

1. **有理数加减法符号法则**（涉及 2 道题）
2. **绝对值概念**（涉及 1 道题）
3. **应用题列式**（涉及 1 道题）

## 四、每题详细批改

### 1. 选择题 ...
[题目/学生答案/批注]

### 2. ...
...

## 五、错题讲解（教师/家长可见）

### 错题 1：q03
**题目**：计算 (-3) + 5 - (-2)

**正解步骤**：
1. 把减法变加法：-3 + 5 + 2
2. 同号合并：(5+2) = 7
3. 异号相减：7 - 3 = 4
4. 结果：4

**学生问题**：把 -(-2) 当作 -2 处理

**讲解脚本**（家长用）：
> 想象减一个负数，相当于"把债收回"，是加的意思。
> 所以减 (-2) = 加 2。

**变式练习**：
- 计算 (-5) + 3 - (-4) = ?
- 计算 7 - (-3) + (-5) = ?

## 六、复习建议

### 给教师
- 建议下节课前 5 分钟复习符号法则
- 建议布置 5 道变式题

### 给家长
- 今晚陪孩子复习 10 分钟符号法则
- 重点：减负数 = 加正数
- 不要批评粗心，要看到概念薄弱

## 七、激励语
> 这次作业正确率 60%，基础概念掌握尚可，主要问题集中在符号变换。  
> 通过今晚 10 分钟的针对性复习，下次有望提到 80% 以上。  
> 继续加油！
```

## 工作流

```
作业输入
  ↓
1. 解析作业
   - 题目列表
   - 学生答案列表
   - 标准答案列表
  ↓
2. 题目-答案对齐
   - 一对一匹配
   - 处理多步题的子步骤
  ↓
3. 逐题批改
   - result: correct / wrong / partial / uncertain
   - score: 0~满分
   - comment_for_student: 1-2 句具体反馈
   - comment_for_teacher: 1 句错因归类
  ↓
4. 错因诊断
   - 调用 misconception-diagnoser
   - 标记 error_type + knowledge_points
  ↓
5. 统计
   - 整体正确率
   - 错因分布
   - 薄弱知识点 TOP 3
  ↓
6. 错题讲解
   - 每道错题生成讲解脚本
   - 区分教师版（详细）和家长版（口语化）
   - 配套变式题
  ↓
7. 复习建议
   - 给教师：课堂复习建议
   - 给家长：家庭辅导建议
  ↓
8. 激励语
   - 基于正确率 + 进步趋势
   - 不空泛、可观察、具体
```

## 实现要点

```python
def review_homework(homework, chapter_id, student_profile, output_format):
    parsed = parse_homework(homework)
    standard = load_standard_answers(chapter_id) or generate(chapter_id)
    aligned = align_qa(parsed, standard)
    
    for item in aligned:
        item.result = grade(item, standard)
        item.score = score(item, standard, rubric)
        item.comment_for_student = build_student_comment(item)
        item.comment_for_teacher = build_teacher_comment(item)
    
    # 错因诊断
    diagnosis = diagnose_errors(aligned, chapter_id, student_profile)
    
    # 讲解
    explanations = build_explanations(aligned, diagnosis, audience='parent')
    
    # 报告
    report = assemble_report(aligned, diagnosis, explanations, output_format)
    return report
```

## 质量标准

| 维度 | 标准 |
|---|---|
| 批改准确率 | ≥ 98% |
| 错因诊断准确率 | ≥ 80% |
| 学生评语具体性 | 不写"再细心点"这种空话，必须指明"哪个步骤" |
| 家长讲解可读性 | 普通家长能直接照着讲 |
| 变式题难度递进 | 至少 1 道原题改编 + 1 道综合 |
| 激励语 | 不空泛、基于数据、可观察 |

## 与其他 skill 的关系

- **上游**：`textbook-ingestion`（提供题目和答案）、`student_profile`（历史错题）
- **调用**：`misconception-diagnoser`（错因）、`math-rubric-grader`（数学步骤分）
- **下游**：`feedback-writer`（最终输出）

## 护栏

1. **不羞辱**：评语不出现"你怎么这么笨"、"这么简单都错"
2. **不空泛**：评语必须具体到题目、步骤、知识点
3. **不替学生做**：错题讲解给家长/教师，不直接给学生完整答案
4. **不脱离实际**：激励语基于真实数据，不夸大进步
5. **不忽略不确定**：OCR 模糊的题标 uncertain，不猜
6. **不直接发布**：报告给教师/家长，不自动推送给学生

## 不要做的事

- 不要给学生写"羞辱式"评语
- 不要把"粗心"作为唯一解释（粗心背后常是概念不熟）
- 不要给完整解题过程（家长/教师自己看）
- 不要做横向比较（"你比小明差"）
