---
name: english-writing-rubric
description: 英语写作评分标准：四档评分（内容/结构/语言/书写），按学段（初中看图写话/高中应用文/高中读后续写）适配。
triggers:
  - 英语教师批改作文
  - 学生需要写作评分
  - 写作模板生成
---

# English Writing Rubric Skill

## 用途

把英语写作批改从"凭感觉打分"提升为"按维度、按权重、按档次"的可重复评分。

## 评分维度（4 维）

| 维度 | 占比 | 评分要点 |
|---|---|---|
| 内容 (Content) | 25% | 完整性、扣题、要点覆盖 |
| 结构 (Organization) | 20% | 段落、逻辑、过渡 |
| 语言 (Language) | 35% | 词汇、语法、句式 |
| 书写 (Handwriting) | 20% | 拼写、标点、卷面 |

## 学段适配

| 学段 | 常见文体 | 字数 |
|---|---|---|
| 小学高年级 | 看图写话、便条 | 30-50 |
| 初中 | 应用文（邮件/通知）、记叙文、议论文 | 60-100 |
| 高中 | 应用文、读后续写、概要写作、议论文 | 100-150 |

## 触发场景

- 教师批改作文
- 学生需要评分
- 写作模板生成
- 单元复习时回顾作文

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| essay | ✅ | 作文文本 |
| prompt | ✅ | 题目/要求 |
| grade | ✅ | 年级 |
| genre | ✅ | 文体 |
| word_count | ❌ | 实际字数 |

## 输出

### `writing_grade.md`

```markdown
# 作文评分：My Hobby

> 学生：xxx | 年级：七年级 | 文体：记叙文
> 字数要求：60-80 | 实际：72

## 一、总分

| 维度 | 满分 | 得分 | 评语 |
|---|---|---|---|
| 内容 | 25 | 22 | 扣题，但 hobbies 描述较简单 |
| 结构 | 20 | 17 | 有开头结尾，中间段稍短 |
| 语言 | 35 | 28 | 句式较单一，多用简单句 |
| 书写 | 20 | 18 | 拼写正确，标点 1 处遗漏 |
| **总分** | **100** | **85** |  |

## 二、档次（中考/高考标准）

| 档次 | 分值 | 本卷 |
|---|---|---|
| 一档（优秀） | 25-27 | |
| 二档（良好） | 21-24 | ✓ |
| 三档（及格） | 16-20 | |
| 四档（不及格） | < 16 | |

## 三、亮点
- 开头自然，引出话题
- 用到 3 个新词（hobby, pastime, leisure）
- 全文 0 拼写错误

## 四、改进点
- 增加 1 个具体例子（学钢琴的细节）
- 用 1-2 个复合句（because / although）
- 结尾可以总结提升

## 五、推荐句型模板

### 开头
- I have a hobby that I enjoy very much.
- Among all my hobbies, ___ is my favorite.
- When it comes to hobbies, I would like to share ___.

### 展开
- First, ___ is interesting because ___.
- For example, ___.
- Moreover, ___ helps me ___.

### 结尾
- In conclusion, ___ is more than a hobby to me.
- I believe ___ will continue to be part of my life.

## 六、范文对比
（给出同题范文，标注差异）
```

## 评分流程

```
输入作文
  ↓
1. 基本检查
   - 字数是否符合要求（±10%）
   - 是否扣题
   - 是否有完整结构
  ↓
2. 内容 (25%)
   - 完整覆盖题目要点
   - 是否有具体细节
   ↓
3. 结构 (20%)
   - 段落划分
   - 逻辑顺序
   - 过渡词使用
  ↓
4. 语言 (35%)
   - 词汇丰富度
   - 语法正确性
   - 句式多样性
  ↓
5. 书写 (20%)
   - 拼写
   - 标点
   - 卷面（图片时）
  ↓
6. 总分 + 档次
   ↓
7. 反馈
   - 亮点
   - 改进点
   - 推荐句型
```

## 实现要点

```python
def grade_essay(essay, prompt, grade, genre):
    # 基础检查
    word_count = count_words(essay)
    word_check = check_word_count(word_count, prompt.required)
    
    # 4 维评分
    content = score_content(essay, prompt, grade)        # 0-25
    organization = score_organization(essay, grade)      # 0-20
    language = score_language(essay, grade)               # 0-35
    handwriting = score_handwriting(essay)                # 0-20
    
    total = content + organization + language + handwriting
    
    # 反馈
    highlights = find_highlights(essay)
    improvements = find_improvements(essay, grade)
    templates = suggest_templates(genre, grade)
    
    return {
        "scores": {
            "content": content,
            "organization": organization,
            "language": language,
            "handwriting": handwriting,
            "total": total
        },
        "highlights": highlights,
        "improvements": improvements,
        "templates": templates
    }
```

## 质量标准

- 4 维评分一致率 ≥ 90%（与教师手改）
- 字数判定准确
- 反馈具体到段落
- 推荐句型可复用

## 护栏

1. **不羞辱学生**：不写"基础太差"
2. **基于文本**：评语必须基于实际作文内容
3. **不空泛**：不写"再努力一点"
4. **不歧视**：评价不涉及学生背景
5. **可执行改进**：每条改进点都能落地
6. **文化敏感**：不评判学生文化背景

## 不要做的事

- 不要把所有错误都列出（选 3-5 个主要）
- 不要写"语法错误太多"这种没价值的评语
- 不要替学生改写全文
- 不要在批注中用"!"等情绪化符号
- 不要因为"漂亮"就给高分
