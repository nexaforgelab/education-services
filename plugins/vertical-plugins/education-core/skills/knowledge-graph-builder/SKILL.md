---
name: knowledge-graph-builder
description: 构建跨章节、跨年级的知识图谱：知识点、前置/后续关系、能力层级、易错关联。是 curriculum-mapper 的超集，支持长链路推理。
triggers:
  - 跨章节知识梳理
  - 单元复习 / 学期复习
  - 学生问"X 之前要学什么 / 之后能用到哪里"
  - Agent 评估"先学 X 还是 Y"
---

# Knowledge Graph Builder Skill

## 用途

构建 **跨章节、跨年级** 的知识图谱，支持：

- 前置知识链（学 X 之前需要什么）
- 后续应用链（学 X 之后能用到哪里）
- 同主题不同章节的关联
- 易错点的知识根源追溯

## 输出

```json
{
  "graph_id": "kg_math_g7_pep_v1",
  "subject": "math",
  "grade_range": "6-9",
  "nodes": [
    {
      "id": "kp_negative_number",
      "name": "负数",
      "grade": 7,
      "chapter": "ch01_s01",
      "level": "concept",
      "curriculum_standard": "理解"
    }
  ],
  "edges": [
    {
      "from": "kp_natural_number",
      "to": "kp_negative_number",
      "type": "prerequisite",
      "strength": 1.0
    },
    {
      "from": "kp_negative_number",
      "to": "kp_rational_arithmetic",
      "type": "leads_to",
      "strength": 0.95
    }
  ]
}
```

## 与 curriculum-mapper 的关系

- `curriculum-mapper`：单章节知识图（轻量）
- `knowledge-graph-builder`：跨章节、跨年级知识图（重量）

调用顺序：先 mapper 看本章，再用 builder 看关联。

## 质量标准

- 节点完整度：覆盖课标 100% 知识点
- 边准确率：≥ 90%
- 支持的查询类型：5+ （前置/后续/同主题/同方法/易错关联）
