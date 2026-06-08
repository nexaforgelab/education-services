---
name: english-word-problem-builder
description: 英语"应用题"构建器：完形填空、阅读理解、短文填空、句型转换等题型的参数化生成与质量保证。
triggers:
  - 英语 worksheet 需要完形填空 / 阅读
  - 单元复习需要综合题
  - 教师需要标准化题型
---

# English Word Problem Builder Skill

## 用途

英语学科的"应用题"题型丰富（完形/阅读/填空/句型转换/翻译/作文），每种题型有不同的构建规则。本 skill 把这些规则系统化、参数化。

## 支持的题型

| 题型 | 难度 | 适用学段 | 构建难度 |
|---|---|---|---|
| 单项选择 | basic | 小学 - 高中 | 低 |
| 完形填空 | medium | 初中 - 高中 | 高 |
| 阅读理解 | medium | 小学 - 高中 | 高 |
| 短文填空 | medium | 初中 | 中 |
| 句型转换 | medium | 初中 | 中 |
| 翻译 | basic | 初中 - 高中 | 中 |
| 选词填空 | medium | 初中 - 高中 | 中 |
| 单词拼写 | basic | 小学 - 初中 | 低 |
| 短文改错 | advanced | 高中 | 高 |
| 书面表达 | advanced | 初中 - 高中 | 高 |

## 触发场景

- 出单元练习
- 单元复习综合卷
- 中高考模拟题

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| question_type | ✅ | 题型 |
| grade | ✅ | 年级 |
| textbook_id | ✅ | 教材 ID |
| chapter_id | ❌ | 章节 |
| difficulty | ✅ | basic / medium / advanced |
| count | ✅ | 数量 |
| theme | ❌ | 主题（如"环保"、"校园"） |

## 输出

```json
{
  "questions": [
    {
      "id": "q1",
      "type": "cloze",
      "difficulty": "medium",
      "stem": "Last weekend, I _____ to the park with my friends.",
      "options": ["go", "went", "have gone", "will go"],
      "correct_answer": "B",
      "explanation": "Last weekend 是过去时间，用一般过去时 went。",
      "page_ref": "教材 p.18",
      "knowledge_points": ["一般过去时"]
    }
  ],
  "passages": [
    {
      "id": "p1",
      "type": "reading",
      "topic": "环保",
      "word_count": 250,
      "level": "medium",
      "content": "...",
      "questions": [...]
    }
  ]
}
```

## 各题型构建规则

### 1. 完形填空（Cloze）

```yaml
cloze:
  word_count: 200-300
  blanks: 10-15
  options_count: 4  # ABCD
  tested_points:
    - 语法（时态、从句、非谓语）
    - 词汇（近义词、固定搭配）
    - 上下文推理
  
  construction:
    1. 选一篇 200-300 词文章
    2. 挖空（每空之间至少 5 个词）
    3. 出 4 个干扰项（语法可能 + 1 正确）
    4. 标注考点
```

**质量要求：**
- 一篇完形只考 2-3 个语法点 + 2-3 个词汇点 + 1-2 个推理点
- 选项必须长度相近、词性相同
- 正确选项不能在语篇中明显优于干扰项

### 2. 阅读理解

```yaml
reading:
  word_count:
    easy: 150-200
    medium: 200-300
    hard: 300-400
  question_count: 4-5
  question_types:
    - 细节（30%）
    - 主旨（20%）
    - 推断（25%）
    - 词义（15%）
    - 态度（10%）
  
  construction:
    1. 选材（教材单元主题或权威语料）
    2. 出 4-5 道题（覆盖 4-5 种题型）
    3. 干扰项基于原文（同义改写、过度推断、无中生有）
```

### 3. 短文填空

```yaml
passage_fill:
  word_count: 80-150
  blanks: 5-10
  word_bank: 6-12 words
  tested_points:
    - 语法填空（用所给词的适当形式）
    - 自由填空（根据上下文）
```

### 4. 句型转换

```yaml
sentence_transformation:
  pairs: 5-10
  formats:
    - 同义句转换：原句 → 用不同句型表达
    - 合并句子：两个简单句 → 一个复合句
    - 改写句子：原句 → 用指定词 / 句型
  
  rules:
    1. 保留核心意思
    2. 答案不唯一但要列首选
    3. 标注考点
```

### 5. 翻译

```yaml
translation:
  items: 5-10
  types:
    - 短语翻译（中 → 英 / 英 → 中）
    - 句子翻译（中 → 英 / 英 → 中）
    - 段落翻译（90-110 字）
  
  rules:
    1. 考点明确
    2. 答案有评分标准（关键词 + 语法）
    3. 难度匹配
```

## 质量标准

| 题型 | 标准 |
|---|---|
| 完形填空 | 一空一个考点，4 干扰项同词性 |
| 阅读理解 | 干扰项能真正干扰，不能"一眼看出" |
| 短文填空 | 单词不超纲，考点覆盖所学 |
| 句型转换 | 答案合理且唯一首选 |
| 翻译 | 关键词完整，语法正确 |

## 实现要点

```python
def build_questions(question_type, grade, textbook_id, chapter_id, difficulty, count, theme):
    if question_type == "cloze":
        return build_cloze(grade, difficulty, count, theme)
    elif question_type == "reading":
        return build_reading(grade, difficulty, count, theme)
    elif question_type == "sentence_transformation":
        return build_sentence_transformation(grade, difficulty, count)
    # ...
    
    # 所有题目必须自检：
    for q in questions:
        validate_question(q)  # 答案可验、考点明确、难度匹配
    return questions
```

## 护栏

1. **不超纲**：考点不超过当前年级
2. **答案可验**：每道题答案唯一
3. **考点明确**：每题标注 knowledge_points
4. **不歧视**：避免涉及宗教、种族、性别歧视
5. **真实自然**：语料来自教材或权威语料
6. **不堆题**：每次最多 5-10 道

## 不要做的事

- 不要出"超纲"语法点
- 不要给"模糊"答案（"两种都可以"）
- 不要堆"高级词汇"
- 不要出"挖坑"题（健康竞争）
- 不要夹带价值观判断

## 与其他 skill 的关系

- **上游**：`textbook-ingestion`（提供教材原句）
- **调用**：`english-misconception-diagnoser`（错因标注）
- **下游**：`worksheet-generator`（整合到练习）
