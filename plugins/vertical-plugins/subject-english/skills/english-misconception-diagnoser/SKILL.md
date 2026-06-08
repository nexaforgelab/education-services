---
name: english-misconception-diagnoser
description: 英语专属误区库：时态/从句/虚拟/非谓语/主谓一致/搭配/词性等常见误区的识别与补救。
triggers:
  - 英语作业错因诊断
  - 错题关联到语法点
  - 教师提问"这个错为什么总犯"
---

# English Misconception Diagnoser Skill

## 用途

沉淀英语学科的 **误区库**——把"这道题做错了"提升为"学生卡在哪个语法点 / 哪个语用习惯"。

## 误区库结构

```yaml
# misconceptions.yaml
- id: MIS-ENG-7-001
  grade: 7
  chapter: 时态
  concept: 一般现在时 vs 现在进行时
  misconception: 把"每天做的事"用现在进行时
  detection_pattern:
    - "I am usually go to school"   # 错
    - "She is like swimming"        # 错
  typical_problem: "I ____ (go) to school every day. → I go (用一般现在时)"
  correct_approach: "I go to school every day."
  remediation:
    analogy: "'每天做的事'是'习惯'，习惯用一般现在时，像每天吃饭'用一般'，不是'正在吃'"
    socratic_questions:
      - "every day 是'频率'，频率用什么时态？"
      - "现在进行时强调'正在做'，那'每天做'是'正在做'吗？"
    practice:
      - "I usually _____ (drink) milk in the morning."
      - "Look! She _____ (dance) in the room."
  page_refs: [ch01_s02_p10]
  severity: high
```

## 英语典型误区（按主题）

### 时态

| 误区 | 学生表现 | 补救 |
|---|---|---|
| 把频率副词搭配现在进行时 | I am usually go to school | 强调"频率 vs 正在" |
| 混淆 since / for | since 5 years / for 2010 | since + 时间点 / for + 时间段 |
| 一般过去时与现在完成时混用 | I have went yesterday | 标 yesterday 用一般过去时 |
| will / be going to 混用 | I am going to rain | will 表预测 / be going to 表计划 |

### 从句

| 误区 | 学生表现 | 补救 |
|---|---|---|
| 宾语从句语序错 | He asked where does she live | 从句用陈述语序 |
| 状语从句时态错 | If he will come, ... | 主将从现 |
| 定语从句关系代词错 | The book which I bought it | which / that 已做宾语，不重复 it |
| 定语从句关系副词错 | I don't know the time when he will come | 表时间 when 正确，但表方式/原因/地点要用 which / why / where |

### 虚拟语气

| 误区 | 学生表现 | 补救 |
|---|---|---|
| wish 后用错时态 | I wish I am rich | wish + 过去时（与现在事实相反） |
| if 虚拟错 | If I will be you, ... | 虚拟条件句用过去时 |
| would rather 后错 | I would rather to go | would rather + 动词原形 |

### 非谓语

| 误区 | 学生表现 | 补救 |
|---|---|---|
| 不定式与动名词混用 | I enjoy to read | enjoy + 动名词 |
| 悬垂分词 | Walking to school, the rain started | 主语不一致 |
| 完成时与不定式 | I should have went | should have done |

### 主谓一致

| 误区 | 学生表现 | 补救 |
|---|---|---|
| 集合名词谓语单复数 | The family are big | 强调整体 vs 个体 |
| 不定代词谓语 | Everyone are here | everyone + 单数 |
| each/either 谓语 | Each of them are ... | each of + 复数名词 + 单数谓语 |

### 词性 / 搭配

| 误区 | 学生表现 | 补救 |
|---|---|---|
| 形容词与副词混用 | She runs quick | 实义动词后用副词 |
| 介词搭配错 | Interested for math | interested in |
| 可数与不可数 | advices / informations | 不可数无 s |
| 冠词漏用 / 滥用 | I like the music | 泛指不用 the |

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
   - high: 核心语法错
   - medium: 单点错
   - low: 拼写 / 标点
  ↓
5. 补救方案
   - 类比
   - 苏格拉底问题
   - 变式练习
```

## 实现要点

```python
def diagnose_english_error(problem, student_answer, correct_answer, grade):
    parsed = parse_problem(problem)
    error_type = classify_error(student_answer, correct_answer, parsed.topic)
    
    # 查误区库
    matches = search_misconceptions(
        grade=grade,
        chapter=parsed.chapter,
        topic=parsed.topic,
        pattern=parsed.pattern
    )
    
    if matches:
        return MisconceptionResult(
            matched=True,
            misconception=matches[0],
            remediation=matches[0].remediation
        )
    else:
        return MisconceptionResult(
            matched=False,
            error_type=error_type,
            remediation=build_generic_remediation(error_type)
        )
```

## 质量标准

- 误区库条目 ≥ 150（每学段 30+）
- 识别准确率 ≥ 80%
- 补救方案可执行

## 护栏

1. **不夸大误区**：常见错误不一定是"误区"，可能是粗心
2. **不忽略情境**：同一个错在不同题可能是不同原因
3. **不羞辱**：写"误区"是教学术语，不是"学生笨"
4. **不歧视**：避免涉及宗教、种族、性别歧视的例句
5. **可解释**：每条误区必须有 detection_pattern 可验证

## 与其他 skill 的关系

- **上游**：`textbook-ingestion`（提供题目）
- **调用**：`misconception-diagnoser`（通用错因）
- **下游**：`homework-reviewer`（批改）、`worksheet-generator`（变式题）

## 维护

误区库按月更新：

- 从作业诊断中提取新误区
- 教师反馈校正
- 学期结束时复盘
- 关注中高考真题新增的考点
