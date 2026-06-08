---
name: learning-profile
description: 维护学生学情画像：基础水平、强项、弱项、错因画像、掌握度、情绪倾向。为其他 skill 提供个性化依据。
triggers:
  - 用户提供学生信息
  - 作业诊断后更新画像
  - 教师/家长主动查询学生画像
  - Agent 决定讲解难度时
---

# Learning Profile Skill

## 用途

维护每个学生的"学情画像"，让 Agent 输出个性化、可追溯。

不是"标签化"，而是"动态的能力地图"。

## 画像内容

```yaml
student_profile:
  id: stu_001
  alias: 小明
  grade: 7
  school_type: public
  subjects:
    math:
      level: 中等          # 基础薄弱 / 中等 / 拔高
      strengths:
        - 计算速度
        - 几何直观
      weaknesses:
        - 符号变换
        - 应用题列式
      mastery_map:
        - kp: 负数
          mastery: 0.85     # 0-1
          last_assessed: 2026-06-01
        - kp: 有理数加减
          mastery: 0.55
          last_assessed: 2026-06-07
      common_error_types:
        - 概念错 (3次)
        - 审题错 (2次)
      learning_notes:
        - 对图像化讲解反应好
        - 喜欢类比
        - 注意力持续 25 分钟
      motivation:
        - 在意分数
        - 不喜欢难题
        - 父母高期待
  english: { ... }
  chinese: { ... }
```

## 触发场景

| 场景 | 写入内容 |
|---|---|
| 用户提供信息 | 基础信息、年级、学科 |
| 作业诊断后 | 更新 mastery_map、common_error_types |
| 教师反馈后 | 更新 strengths / weaknesses / motivation |
| 单元复习后 | 更新整体掌握度 |

## 输出接口

```python
# 其他 skill 调用
def get_profile(student_id: str) -> StudentProfile
def get_mastery(student_id: str, kp: str) -> float
def get_weak_kps(student_id: str, threshold: float = 0.6) -> List[str]
def get_strong_kps(student_id: str, threshold: float = 0.8) -> List[str]
def update_profile(student_id: str, updates: dict)
def get_recent_errors(student_id: str, days: int = 7) -> List[Error]
```

## 护栏

1. **不贴标签**：level=基础薄弱 ≠ "学生笨"，是 "目前该学科处于基础阶段"
2. **可重置**：学生进步后，画像要能更新
3. **可解释**：每个 mastery 分数必须能追溯到具体测试 / 作业
4. **隐私优先**：学生姓名用 alias，不写真名
5. **不外传**：画像数据仅 Agent 内使用

## 不要做的事

- ❌ 不要给学生加"聪明"、"勤奋"、"调皮"等性格标签
- ❌ 不要基于单次考试给学生贴"差生"标签
- ❌ 不要把 mastery 数值直接展示给学生（会制造焦虑）
- ❌ 不要把家长情绪带入画像（"家长不重视"不该进画像）

## 与其他 skill 关系

- `misconception-diagnoser` 写入
- `homework-reviewer` 写入
- `pedagogy-method` 读取
- `lesson-planner` 读取
- `parent-report-writer` 读取
- `unit-review-agent` 读取
