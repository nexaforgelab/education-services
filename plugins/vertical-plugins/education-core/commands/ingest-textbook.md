---
name: ingest-textbook
description: 解析教材 PDF，建立教材索引、章节结构、知识点图谱。
usage: /ingest-textbook <pdf_path> <subject> <grade> <version>
---

# /ingest-textbook 命令

把一本教材 PDF 变成可被 Agent 引用、可被向量检索的结构化数据。

## 语法

```
/ingest-textbook <pdf_path> <subject> <grade> <version>
```

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| pdf_path | ✅ | PDF 文件绝对路径或 S3/MinIO URL |
| subject | ✅ | math / english / chinese / science / physics / chemistry |
| grade | ✅ | "1" ~ "12" |
| version | ✅ | 人教版 / 北师大版 / 苏教版 / 沪教版 等 |

## 行为

调用 `textbook-ingestion` skill 执行：

1. 预检 PDF（页数、可读性、是否加密）
2. 提取目录、章节、页码
3. 切分 block（concept/example/exercise/image/table/summary）
4. 公式、图表处理
5. 写入 PostgreSQL + pgvector
6. 生成 `textbook_manifest.json`

## 输出

```
✅ 教材解析完成

教材：数学 七年级 上册（人教版）
页数：156
章节：6 章 27 节
向量索引：874 条
教材 ID：math_g7_vol1_pep_2024

manifest: out/textbook_manifest.json
```

## 错误处理

- PDF 不存在 → 提示用户检查路径
- 加密 PDF → 提示提供密码
- 没有目录 → 降级为基于字体 + 标题规则识别，提示用户
- 扫描版 → 走 OCR 流程，耗时较长

## 示例

```
/ingest-textbook ./samples/math_g7_pep.pdf math 7 人教版
```

## 关联命令

- `/lesson-plan` 备课（依赖已入库教材）
- `/unit-review` 单元复习
- `/worksheet` 出题

## 后端实现

```python
# scripts/ingest_textbooks.py
def main():
    args = parse_args()
    manifest = ingest(args.pdf_path, args.subject, args.grade, args.version)
    save_manifest(manifest, out_dir='out/')
    print(f"教材 ID: {manifest['textbook_id']}")
```
