---
name: explain-to-parent
description: 生成家长能听懂、能讲给孩子听的解释。
usage: /explain-to-parent <chapter_or_concept>
---

# /explain-to-parent 命令

把教材语言翻译成家长语言，输出"今晚 10 分钟就能讲"的家庭辅导脚本。

## 语法

```
/explain-to-parent <chapter_or_concept>
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| chapter_or_concept | ✅ | 章节名 / 概念名 / 知识点 ID |

## 行为

调用 `parent-friendly-explanation` skill（家长工作流）和 `home-coaching-script` skill：

1. 定位教材章节或概念
2. 翻译为家长语言（生活比喻）
3. 生成 3-5 个启发式问题
4. 给出 10 分钟家庭练习
5. 给出鼓励话术
6. 给出"不要怎么做"清单

## 输出

```
out/parent_explain/
├── what_learned.md         # 今天学什么
├── parent_explanation.md   # 家长能懂的解释
├── how_to_check.md         # 怎么判断孩子懂没懂
├── dont_do_this.md         # 不要怎么讲
├── questions_to_ask.md     # 可以怎么问
├── prompts_when_stuck.md   # 孩子卡住怎么提示
├── ten_min_practice.md     # 10 分钟家庭练习
└── encouragement.md        # 鼓励话术
```

## 风格

- 口语化：像隔壁家长聊天
- 生活化：买菜、找零、走路等比喻
- 具体化：每句话家长能直接照做
- 不焦虑：永远先说"做得好的"

## 示例

```
/explain-to-parent 有理数 加法
```

## 边界

- 不替家长做教育决策
- 不评判其他家长做法
- 不评判学校/教师
- 不替孩子做作业
