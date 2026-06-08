---
name: english-grammar-explainer
description: 英语语法解释：基于教材语法点的三层讲解（直观/规则/例句），覆盖时态、从句、虚拟语气、非谓语等核心语法。
triggers:
  - 英语教师说"讲一下现在完成时"
  - 家长问"虚拟语气怎么给孩子讲"
  - 错题诊断关联到语法点
---

# English Grammar Explainer Skill

## 用途

把英语语法点从"教条规则"翻译成"学生真能理解、能用对"的语言。

## 三层讲解

| 层级 | 名称 | 内容 | 面向 |
|---|---|---|---|
| L1 | 直观 | 时间线/场景图/中文类比 | 家长 + 基础薄弱学生 |
| L2 | 规则 | 形式化规则、构成公式 | 中等学生 |
| L3 | 例句 | 教材原句 + 变式 | 所有学生 |

## 触发场景

- 教师讲新语法点
- 错题诊断关联到语法
- 家长问"怎么给孩子讲"
- 单元复习

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| grammar_point | ✅ | 语法点（如"现在完成时"） |
| grade | ✅ | 年级 |
| textbook_id | ✅ | 教材 ID |
| chapter_id | ❌ | 章节 |
| audience | ✅ | teacher / parent / student |
| common_mistakes | ❌ | 学生常见错 |

## 输出

### 示例：现在完成时

```markdown
# 现在完成时（Present Perfect）

## L1 直观（家长能讲）

**一句话：**
> 过去发生的事 + 现在还有影响 → 用现在完成时

**时间线：**
```
过去  ─── 现在  ─── 未来
   │       │
   │       └─ 现在还有影响吗？
   │           │
   │           是 → 现在完成时：I have lost my key.
   │           （我丢了钥匙，**现在**还没找到）
   │
   └─ 过去某点发生的事
       │
       强调"什么时候发生" → 一般过去时：I lost my key yesterday.
       （昨天丢的，**现在**找没找回来不知道）
```

**中文类比：**
> "我已经吃了" ≠ "我吃了"
> "我已经吃了" = "吃了" + "现在不饿了" = 现在完成时
> "我吃了" = 过去某时吃了 = 一般过去时

## L2 规则（中等学生）

**构成：** have/has + 过去分词
- I/You/We/They → have + done
- He/She/It → has + done

**标志词：**
- already / yet / just / ever / never
- since + 时间起点 / for + 时间段
- so far / up to now / recently / lately
- How many times ... ?

**用法：**
1. 过去发生 + 现在有影响
2. 从过去持续到现在
3. 经历（有过 ... 的经验）
4. 结果（just / already）

## L3 例句（教材）

教材 p.36：
- I **have lived** in Beijing for five years.（持续到现在）
- She **has visited** Paris three times.（经历）
- He **has just finished** his homework.（结果）

变式（基础 → 中等 → 综合）：
- 基础：I have eaten.
- 中等：I have eaten lunch already.
- 综合：I have eaten lunch, so I am not hungry now.

## 常见错

❌ I have went to school.（错：went → gone）
❌ I have went to school yesterday.（错：现在完成时不与 yesterday 连用）
❌ I am living here for 5 years.（错：持续到现在用 have lived）

## 真题示例

- 20XX 中考：I _____ (read) the book twice. 答案：have read
- 20XX 高考：By the time he arrives, I _____ (finish). 答案：will have finished
```

## 核心语法点清单

### 初中

- 时态：一般现在/过去/将来、现在进行/完成、过去进行/完成
- 从句：宾语从句、状语从句、定语从句（基础）
- 被动语态（基础）
- 非谓语：动词不定式作宾语/宾补
- 情态动词 can/could/may/might/must/have to

### 高中

- 全部时态
- 三类从句（宾/状/定）
- 虚拟语气
- 非谓语（不定式/动名词/分词）
- 主谓一致
- 强调句 / 倒装句

## 工作流

```
输入 grammar_point
  ↓
1. 教材定位
   - 找语法点定义（page_ref）
   - 找典型例句
  ↓
2. L1 直观
   - 时间线 / 场景图
   - 中文类比
  ↓
3. L2 规则
   - 形式化定义
   - 标志词
   - 构成公式
  ↓
4. L3 例句
   - 教材原句
   - 难度递进变式
  ↓
5. 常见错
   - 调误区库
  ↓
6. 真题（可选）
```

## 实现要点

```python
def explain_grammar(point, grade, textbook_id, audience):
    blocks = load_textbook_blocks(textbook_id, point.chapter)
    
    return {
        "L1_intuitive": build_intuitive(point, blocks),
        "L2_rule": build_formal_rule(point),
        "L3_examples": build_examples(point, blocks),
        "common_mistakes": load_misconceptions("english", point.id),
        "exam_questions": search_exam_corpus(point),
        "page_refs": extract_page_refs(blocks)
    }
```

## 质量标准

- L1 类比必须准确（不强行类比）
- L2 规则必须形式化（用公式或表格）
- L3 例句 100% 引用教材页码
- 常见错 80%+ 命中误区库
- 难度匹配年级

## 护栏

1. **不教条**：语法不是死规则，是语用习惯
2. **不堆规则**：每点只讲核心 1-2 条规则
3. **不脱离语境**：例句必须真实自然
4. **不歧视**：例句避免涉及宗教、种族、性别歧视
5. **不超纲**：高中语法不在初中讲

## 不要做的事

- 不要把语法讲成"必须死记的规则"
- 不要用"专有名词"吓学生
- 不要堆"高级例句"（如 Shakespeare 原句）
- 不要给"语法术语"不给"中文解释"
- 不要脱离教材讲"超纲"语法
