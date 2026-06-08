---
name: english-vocabulary-builder
description: 英语词汇专项：基于教材生词表的深度加工——词根词缀、搭配、例句、近义词辨析、艾宾浩斯复习曲线。
triggers:
  - 英语教师说"处理生词表"
  - 家长问"怎么帮孩子记单词"
  - 单元复习需要词汇清单
---

# English Vocabulary Builder Skill

## 用途

把"教材生词表"提升为"可记忆、可运用、可复习"的词汇学习包。

普通死记硬背：拼写 + 中文意思 → 30 天后遗忘 80%
本 skill 输出：拼写 + 读音 + 词根词缀 + 搭配 + 例句 + 复习曲线 → 30 天后保持 70%+

## 触发场景

- 新单元开始，需要处理生词表
- 学生单词记不住
- 家长问"怎么帮孩子背单词"
- 单元复习时回顾

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| word_list | ✅ | 生词列表 [{word, pos_zh, pos_en, page_ref}] |
| grade | ✅ | 年级 |
| textbook_id | ✅ | 教材 ID |
| chapter_id | ✅ | 章节 ID |
| target_retention | ❌ | 默认 30 天 70% |

## 输出

### `vocabulary_deck.md`（学生用）+ `vocabulary_teacher.md`（教师用）

每词一卡：

```markdown
## abandon /əˈbændən/ v. 放弃；遗弃

### 词根词缀
- a-（前缀：去、向）+ ban（禁令）+ -don
- 词源：ban 本身有"禁止"之意，加前缀变成"完全禁止去做"，引申为"放弃"

### 教材原句
- The villagers had to **abandon** their homes because of the flood.
- 教材 p.42 第 3 段

### 常用搭配
- abandon doing sth 放弃做某事
- abandon sb to fate 抛弃某人于命运
- with abandon 放纵地
- abandon oneself to 沉溺于

### 同义辨析
| 词 | 含义 | 区别 |
|---|---|---|
| abandon | 永久放弃、抛弃 | 强调完全、彻底 |
| give up | 放弃 | 口语化，可放弃想法、习惯 |
| desert | 抛弃（人）、擅离（岗位） | 强调不负责任 |
| quit | 停止、辞职 | 强调主动停止 |

### 派生词
- abandoned adj. 被遗弃的
- abandonment n. 放弃
- unabandoned adj. 不放弃的（罕用）

### 艾宾浩斯复习点
- 第 1 次：当天
- 第 2 次：第 2 天
- 第 3 次：第 4 天
- 第 4 次：第 7 天
- 第 5 次：第 15 天
- 第 6 次：第 30 天

### 一句话记忆
- "乐队 **abandon** 了主唱，主唱被 **desert** 在沙漠"

### 高考 / 中考真题
- 20XX 年 XX 卷：用 abandon 的适当形式填空（答案见末尾）

### 写作应用
- 适用主题：环保（abandon bad habits）、勇气（never abandon hope）
- 高分句型：It is never too late to abandon / One should not abandon ...
```

## 工作流

```
输入生词表
  ↓
1. 教材核查
   - 每个词在教材原文中找 1-2 个例句（带 page_ref）
   - 标 [教材原文] 置信度
  ↓
2. 词根词缀分析
   - 拆前缀、词根、后缀
   - 词源故事（如有助记忆）
  ↓
3. 搭配与派生
   - 常见搭配 3-5 个
   - 派生词 2-4 个
  ↓
4. 同义辨析
   - 找出 2-3 个近义词
   - 用表格说明差异
  ↓
5. 复习曲线
   - 按艾宾浩斯安排 6 个复习点
  ↓
6. 写作应用
   - 推荐主题 + 高分句型
  ↓
7. 真题（可选）
   - 匹配近 5 年中高考真题
```

## 实现要点

```python
def build_vocabulary(word_list, grade, textbook_id, chapter_id):
    deck = []
    for word_info in word_list:
        entry = {
            "word": word_info["word"],
            "ipa": get_ipa(word_info["word"]),  # CMU dict
            "etymology": analyze_etymology(word_info["word"]),
            "examples": search_textbook(word_info["word"], textbook_id, chapter_id),
            "collocations": get_collocations(word_info["word"]),
            "synonyms": get_synonyms(word_info["word"], grade),
            "derivatives": get_derivatives(word_info["word"]),
            "ebbinghaus_schedule": ebbinghaus_30days(),
            "memory_aid": generate_memory_aid(word_info["word"]),
            "writing_application": suggest_writing(word_info["word"]),
            "exam_questions": search_exam_corpus(word_info["word"]),
            "page_ref": word_info.get("page_ref")
        }
        deck.append(entry)
    return deck
```

## 质量标准

- 教材原句 100% 引用页码
- 词根词缀准确（基于权威词源词典）
- 搭配不超 5 个，避免堆砌
- 同义辨析用表格清晰呈现
- 一句话记忆点 ≤ 20 字
- 真题标年份和试卷

## 护栏

1. **不编造词源**：词源基于权威词源词典（OED、ETymology Online）
2. **不堆例句**：每词 1-2 句就够，多了反而记不住
3. **不夸大作用**：不写"记住这个词高考必考"
4. **不脱离语境**：例句必须来自教材或权威语料
5. **不歧视**：例句避免涉及宗教、种族、性别歧视

## 不要做的事

- 不要把所有派生词都列出（除非高频）
- 不要把所有近义词都列出（2-3 个就够）
- 不要写"高频考点"（除非有真题数据支撑）
- 不要给 5+ 句长难句例句
- 不要把所有真题都列出（精选 1-2 道）

## 依赖

- CMU Pronouncing Dictionary（音标）
- WordNet（同义词、反义词）
- Etymology Online（词源）
- 教材原句库
- 中高考真题语料库
