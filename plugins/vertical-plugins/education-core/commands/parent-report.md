---
name: parent-report
description: 生成一份家长沟通报告。
usage: /parent-report <student_id_or_profile> <period>
---

# /parent-report 命令

把学生的学习情况翻译成家长能看懂、能执行的报告。

## 语法

```
/parent-report <student_id_or_profile> <period>
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| student_id_or_profile | ✅ | 学生 ID 或画像描述 |
| period | ✅ | weekly / monthly / unit / 自定义时间段 |

## 行为

调用 `parent-report-writer` skill 和 `misconception-diagnoser` skill：

1. 汇总学生期间内学习数据
2. 翻译为家长语言
3. 提炼亮点 + 改进点
4. 给出"今晚 10 分钟"辅导脚本
5. 给出"不要怎么做"清单
6. 给出下一步计划
7. 给出鼓励语
8. 标注何时寻求专业支持

## 输出

```
out/parent_report/
├── parent_report.md        # 主报告
├── strengths.md            # 亮点
├── growth_areas.md         # 改进点
├── coaching_script.md      # 10 分钟辅导脚本
├── donts.md                # 不要做清单
├── next_week_plan.md       # 下周计划
└── pro_help_signals.md     # 何时寻求专业支持
```

## 风格

- 口语化、生活化
- 不焦虑、不空泛
- 具体可执行
- 不评判人格
- 不挑拨家校关系

## 报告结构（必备 8 节）

1. 本周学了哪些内容
2. 孩子掌握得怎么样（亮点 + 改进）
3. 孩子卡在哪里（用大白话讲）
4. 家长可以怎么帮（今晚 10 分钟）
5. 家长不要这样做
6. 下周要做什么
7. 本周一句话总结
8. 需要专业支持吗

## 护栏

- 不写"孩子笨"、"不上心"
- 不写"老师讲得不好"
- 不写"必须报辅导班"
- 不评判学生人格
- 不泄露具体学校/班级/同学名

## 示例

```
/parent-report stu_001 weekly
/parent-report "小明 七年级" monthly
```

## 边界

- 不替家长做教育决策
- 不评判学校/教师
- 不替孩子做作业
- 不写超长文档
