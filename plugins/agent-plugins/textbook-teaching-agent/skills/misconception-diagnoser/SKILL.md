---
name: misconception-diagnoser
description: 基于学生答题/作业，识别常见错因类型（概念错/审题错/计算错/步骤缺失/表达不规范），匹配已知误区库，给出针对性补救讲解。
triggers:
  - 用户提交学生作业
  - /diagnose-homework 命令
  - homework-reviewer 需要分类错因
  - 单元复习时回顾学生错题
---

# Misconception Diagnoser Skill

## 用途

把"这道题做错了"提升为"这个学生卡在哪个知识点 / 哪个思维环节"，并给出可执行的补救方案。

教育研究表明，学生反复错同类型题 80% 不是粗心，而是某个底层概念或方法有偏差。

## 触发场景

- 学生提交作业图片 / 文字答案
- 单元复习时回顾错题集
- 教师主动问"这道题为什么学生总是错"
- `/diagnose-homework <homework> <chapter>`

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| homework_text | ✅ 或 | 题目 + 学生答案 + 正确答案 |
| homework_image_url | ✅ 或 | 作业图片（OCR 后转文本） |
| chapter_id | ✅ | 涉及的章节 |
| student_profile | ❌ | 学生画像，匹配错因历史 |
| curriculum_map | ❌ | 涉及的知识点地图 |
| standard_answer | ❌ | 若 Agent 没识别到，教师可手动补充 |

## 输出

### `diagnosis.json`

```json
{
  "homework_id": "hw_2026_06_07_001",
  "student_id": "stu_001",
  "diagnosed_at": "2026-06-07T10:30:00Z",
  "overall": {
    "total_questions": 10,
    "wrong_count": 4,
    "wrong_rate": 0.4,
    "mastery_estimate": "partially_mastered"
  },
  "items": [
    {
      "question_id": "q03",
      "question_text": "计算 (-3) + 5 - (-2) = ?",
      "student_answer": "0",
      "correct_answer": "4",
      "is_correct": false,
      "error_type": "concept_error",
      "error_type_detail": "符号法则：减负数等于加正数",
      "knowledge_points": ["有理数加减法", "符号法则"],
      "likely_cause": "把 '减负数' 当成 '减一个比 0 小的数'，没有先化简符号",
      "misconception_match": "MIS-MATH-7-001: 把减法统一为加法时符号处理错误",
      "severity": "high",
      "remediation": {
        "explanation": "...",
        "socratic_questions": [
          "看到 '减负数'，第一步要做什么？",
          "'-(-2)' 等于什么？",
          "把每个减法都变成加法，原式变成什么？"
        ],
        "variation_problems": [
          "计算 (-5) + 3 - (-4) = ?",
          "计算 7 - (-3) + (-5) = ?"
        ],
        "review_plan": "今天复习符号法则 10 分钟，做 5 道变式题"
      }
    }
  ],
  "summary": {
    "main_error_types": ["concept_error", "calculation_error"],
    "weak_knowledge_points": ["有理数加减法符号法则"],
    "strong_knowledge_points": ["正负数判定"],
    "recommended_focus": "优先补习有理数符号法则 1 课时",
    "encouragement": "整体正确率 60%，基础知识掌握尚可，主要问题集中在符号变换"
  }
}
```

## 错因分类

```
error_type:
  - concept_error       # 概念 / 原理没掌握
  - calculation_error   # 运算过程错误
  - careless_error      # 审题 / 抄写 / 漏看条件
  - method_error        # 解题方法选错
  - step_missing        # 步骤缺失（缺过程）
  - expression_error    # 表达不规范（单位/格式/术语）
  - prerequisite_gap    # 前置知识缺失
  - transfer_error      # 类比迁移错误（错把 A 题方法用到 B 题）
```

## 工作流

```
作业输入
  ↓
1. 题目-答案对齐
   - OCR / 文本提取
   - 题目 ID 化（q01, q02, ...）
   - 学生答案 vs 标准答案对齐
   - 标记 is_correct
  ↓
2. 错题筛选
   - 错误题进入诊断
   - 模糊答案（如图片模糊）标记 uncertain=true
  ↓
3. 错误类型分类
   - 错一道 → 错因分析
   - 错误类型枚举见上
   - 多错一道 → 多错因可能并存
  ↓
4. 知识图谱匹配
   - 把题对应到 curriculum_map 的 knowledge_points
   - 标记"薄弱知识点"
  ↓
5. 误区库匹配
   - 调用 vertical plugin 里的误区库
     * math-misconception-diagnoser
     * english-misconception-diagnoser
   - 命中已知误区 → 复用解释模板
   - 未命中 → 走通用诊断逻辑
  ↓
6. 严重度评估
   - high: 核心概念错，影响后续
   - medium: 单点错，可补救
   - low: 粗心
  ↓
7. 补救方案生成
   - 启发式提问（socratic_questions）
   - 变式题（variation_problems，难度递进）
   - 复习计划（review_plan）
  ↓
8. 整体总结
   - 主错因分布
   - 强弱知识点
   - 一句鼓励（不贴标签）
```

## 误区库结构

```yaml
# subject-math/skills/math-misconception-diagnoser/misconceptions.yaml
- id: MIS-MATH-7-001
  grade: 7
  chapter: "有理数"
  concept: "有理数加减法"
  misconception: "减负数时未变号"
  detection_pattern: "(-a) - (-b) → student writes -a - b"
  typical_problem: "(-3) - (-5) = -8"
  correct_approach: "(-3) - (-5) = -3 + 5 = 2"
  remediation_template: "..."
  page_refs: ["ch01_s05_p18"]
```

## 实现要点

```python
def diagnose(homework, chapter_id, student_profile):
    parsed = parse_homework(homework)  # 题目+答案对齐
    misconceptions_db = load_misconceptions(subject, chapter_id)
    
    for item in parsed.wrong_items:
        # 1. 错因分类
        item.error_type = classify_error(item, misconceptions_db)
        # 2. 知识图谱匹配
        item.knowledge_points = match_knowledge(item, curriculum_map)
        # 3. 误区匹配
        item.misconception_match = match_misconception(item, misconceptions_db)
        # 4. 补救方案
        item.remediation = build_remediation(item, misconceptions_db)
    
    summary = summarize(parsed, student_profile)
    return build_diagnosis(parsed, summary)
```

## 质量标准

| 维度 | 标准 |
|---|---|
| 题目-答案对齐 | ≥ 95% |
| 错因分类准确率 | ≥ 80%（教师抽检） |
| 知识图谱命中 | 100% 错题都有对应知识点 |
| 启发式提问质量 | 不直接给答案，3-5 个递进问题 |
| 变式题难度递进 | 基础 → 中等 → 综合 |
| 鼓励语 | 不空泛、不贴标签、具体可观察 |

## 与其他 skill 的关系

- **上游**：`textbook-ingestion`（提供题目+页码）、`student_profile`（错题历史）
- **并行**：`math-misconception-diagnoser`（学科垂直误区库）
- **下游**：`homework-reviewer`（整合到作业报告）、`worksheet-generator`（生成变式题）

## 护栏

1. **不羞辱学生**：错因分析只针对知识点，不针对人格
2. **不替学生下结论**：写"建议补习 X"，不写"学生不会 X"
3. **不忽略模糊题**：OCR 模糊必须明确标记，不能猜
4. **不替学生答题**：补救讲解用启发式，不写完整解题过程
5. **不过度诊断**：粗心也可能真是粗心，不要"为赋新词强说愁"
6. **不贴标签**：避免"这个学生逻辑差"、"粗心大意"等性格化判断

## 不要做的事

- 不要给完整解题过程（学生启发式讲解由 math-stepwise-socratic-tutor 负责）
- 不要给最终排名或分数（教师自行判断）
- 不要跨学科推断（数学错题不要推断英语能力）
- 不要替家长做教育决策（写建议而不是命令）
