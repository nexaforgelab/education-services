---
name: curriculum-mapper
description: 基于 textbook-ingestion 的输出，构建章节级知识图谱：核心概念、前置知识、后续知识、重点、难点、易错点、能力目标。
triggers:
  - 用户指定章节后需要建立知识点地图
  - /lesson-plan / /worksheet / /diagnose-homework 命令的早期阶段
  - Agent 需要评估学生是否具备学习本章的基础
---

# Curriculum Mapper Skill

## 用途

把教材章节的"内容列表"提升为"知识结构"——明确：

- 这一节要学什么（核心概念）
- 学习它需要先学什么（前置知识）
- 学完之后能干什么（能力目标）
- 后续会用到哪里（后续知识）
- 学生最容易在哪里卡住（易错点 / 难点）

**这是 Agent 评估"学生水平是否适合"和"讲解要从哪里开始"的基础。**

## 触发场景

- 主 Agent 完成 `Textbook Grounding` 之后
- 收到 `/lesson-plan` / `/worksheet` / `/diagnose-homework` 命令
- 单元复习 / 跨章节梳理
- 学情诊断时需要回溯知识链

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| textbook_id | ✅ | 已入库的教材 |
| chapter_id | ✅ | 章节 id |
| section_id | ❌ | 节 id，留空 = 整章 |
| student_profile | ❌ | 学生画像（影响重点/难点选择） |
| grade | ✅ | 年级（影响课程标准对照） |

## 输出

### `curriculum_map.json`

```json
{
  "chapter_id": "ch01",
  "section_id": "ch01_s01",
  "title": "正数和负数",
  "core_concepts": [
    {
      "name": "正数",
      "definition": "大于 0 的数叫正数",
      "difficulty": "easy",
      "page_refs": [2, 3]
    },
    {
      "name": "负数",
      "definition": "小于 0 的数叫负数",
      "difficulty": "easy",
      "page_refs": [2, 3]
    }
  ],
  "prerequisites": [
    {
      "name": "自然数",
      "why": "理解负数需要先理解数轴方向和 0 的位置",
      "where_taught": "小学"
    },
    {
      "name": "0 的意义",
      "why": "0 既不是正数也不是负数，是分界点",
      "where_taught": "小学"
    }
  ],
  "followups": [
    { "name": "有理数加减", "chapter_id": "ch01_s05" },
    { "name": "数轴", "chapter_id": "ch01_s02" }
  ],
  "key_points": ["正负数的判定", "0 的特殊性", "用正负数表示相反意义的量"],
  "difficulties": ["相反意义的量的识别（温度 vs 海拔 vs 收支）"],
  "common_misconceptions": [
    {
      "concept": "负数",
      "misconception": "认为带负号的数一定比正数小（忽略绝对值大小）",
      "manifestation": "认为 -10 比 -1 小",
      "remediation": "通过数轴直观演示"
    }
  ],
  "learning_objectives": [
    "能判断一个数是正数、负数还是 0",
    "能用正负数表示现实生活中相反意义的量",
    "能举例说明 0 在正负数体系中的特殊地位"
  ],
  "estimated_minutes": 45,
  "confidence": {
    "core_concepts": 0.92,
    "prerequisites": 0.85,
    "misconceptions": 0.78
  }
}
```

## 工作流

```
章节定位
  ↓
1. 拉取章节内容
   - 从 textbook_blocks 拉取本节所有 block
   - 区分：定义 / 概念 / 例题 / 练习 / 小结
  ↓
2. 核心概念抽取
   - 从"定义"、"概念"类 block 抽取
   - 提取：概念名 + 形式化定义 + 教材原文引用
  ↓
3. 前置知识推断
   - 检索教材中"为了理解 X，我们需要 Y"的暗示
   - 对照课程标准（义务教育数学课程标准 2022 版）
   - 检查 student_profile 中已掌握知识点
  ↓
4. 后续知识关联
   - 扫描同章后面节 + 下一章
   - 标出"X 在 ... 章节会进一步学习"
  ↓
5. 重难点 + 易错点
   - 教材中的"想一想"、"议一议"、"注意"标记
   - 学科垂直 skill（math-misconception-diagnoser）补充
   - 历史错题数据（若学生有）
  ↓
6. 学习目标
   - 用 ABCD 模型：Audience + Behavior + Condition + Degree
   - 动词要可观察：判断 / 写出 / 解释 / 应用 / 分类
  ↓
7. 置信度
   - 教材原文 → 高
   - 教材 + 课程标准 → 中
   - 仅靠通用知识 → 低（标出来让用户审）
```

## 实现要点

```python
# skill 核心伪代码
def map_curriculum(textbook_id, chapter_id, section_id, student_profile):
    blocks = load_blocks(textbook_id, chapter_id, section_id)
    concepts = extract_concepts(blocks)        # 基于规则 + LLM
    prereqs = infer_prerequisites(concepts, curriculum_standard)
    followups = scan_followups(textbook_id, chapter_id)
    misconceptions = load_misconception_db(subject, chapter_id)
    objectives = write_objectives(concepts, level=student_profile.level)
    return build_curriculum_map(...)
```

## 质量标准

| 维度 | 标准 |
|---|---|
| 核心概念完整度 | ≥ 90%（对照教材目录） |
| 前置知识准确率 | ≥ 85% |
| 易错点命中率 | 至少能命中该学科垂直 skill 中已知的 Top 5 |
| 学习目标动词化 | 100% 使用可观察动词 |
| 引用页码 | 100% 概念带 page_refs |

## 与其他 skill 的关系

- **上游**：`textbook-ingestion`（提供 blocks）
- **下游**：
  - `pedagogy-method`（基于本 skill 选择教学策略）
  - `lesson-planner`（基于本 skill 生成教案）
  - `math-misconception-diagnoser`（基于本 skill 诊断）
  - `worksheet-generator`（基于本 skill 出题）

## 护栏

1. **不编造概念**：抽取的概念必须能在教材原文中找到
2. **不夸大难度**：避免把"重点"等同于"难点"
3. **不贴学生标签**：易错点是"普遍现象"，不要写"X 学不会"
4. **置信度透明**：低置信度内容必须标注，让教师/家长判断
5. **课程标准依据**：跨年级前置知识必须符合课程标准

## 不要做的事

- 不要直接生成讲解（交给 pedagogy-method 和 math-concept-explainer）
- 不要给具体教案步骤（交给 lesson-planner）
- 不要直接出练习题（交给 worksheet-generator）
- 不要给个性化建议（那是 pedagogy-method + student_profile 的事）
