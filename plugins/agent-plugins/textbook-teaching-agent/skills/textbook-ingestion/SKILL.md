---
name: textbook-ingestion
description: 解析教材 PDF 文档，识别目录、页码、章节、例题、练习、图表，生成结构化索引和 textbook_manifest.json。教材驱动的所有后续 skill 都依赖此 skill 的输出。
triggers:
  - 用户上传 PDF 教材
  - /ingest-textbook 命令
  - Agent 启动时需要定位章节
---

# Textbook Ingestion Skill

## 用途

把一本教材 PDF 变成可被 Agent 引用、可被向量检索、可被知识图谱构建的结构化数据。

**为什么这个 skill 最关键**：教育 Agent 输出的"教材依据"完全依赖这一层的准确度。教材页码错 1 页，整个引用就不可信。

## 触发场景

- 用户首次上传教材 PDF
- 用户说"导入教材"、"解析教材"、"我要用 XX 教材"
- `/ingest-textbook <pdf_path> <subject> <grade> <version>`
- Agent 在 `textbook-reader` subagent 流程中需要定位章节

## 输入

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pdf_path | str | ✅ | PDF 文件绝对路径或 S3/MinIO URL |
| subject | str | ✅ | math / english / chinese / science / physics / chemistry |
| grade | str | ✅ | "1" ~ "12" |
| version | str | ✅ | 人教版 / 北师大版 / 苏教版 / 沪教版 等 |
| ocr_lang | str | ❌ | 默认 chi_sim+eng |

## 输出

### 1. `textbook_manifest.json`（必备）

```json
{
  "textbook_id": "math_g7_vol1_pep_2024",
  "title": "数学 七年级 上册",
  "subject": "math",
  "grade": "7",
  "version": "人教版",
  "publisher": "人民教育出版社",
  "edition_year": 2024,
  "total_pages": 156,
  "file_hash": "sha256:...",
  "ingested_at": "2026-06-07T10:00:00Z",
  "chapters": [
    {
      "chapter_id": "ch01",
      "title": "有理数",
      "page_start": 1,
      "page_end": 38,
      "sections": [
        {
          "section_id": "ch01_s01",
          "title": "正数和负数",
          "pages": [2, 3, 4],
          "concepts": ["正数", "负数", "相反意义的量"],
          "examples": [
            { "id": "ex01", "page": 3, "text": "..." }
          ],
          "exercises": [
            { "id": "ex_group_01", "page": 4, "type": "practice", "items": 4 }
          ]
        }
      ]
    }
  ]
}
```

### 2. `textbook_blocks`（数据库行）

每页切分为多个 block：

```
textbook_blocks:
  id
  textbook_id
  chapter_id
  section_id
  page_number
  block_type  # concept | example | exercise | image | table | summary | definition
  content     # 文本
  bbox        # 页面坐标 [x0, y0, x1, y1]
  image_url   # 图片 OCR 结果图
  embedding_id  # 向量索引 id
```

### 3. `vector_index` 条目

每个 block 写入 `vector_index`，metadata 包含 `textbook_id / chapter_id / section_id / page_number / block_type`。

## 工作流

```
PDF 上传
  ↓
1. 预检
   - 验证文件存在、可读、未加密
   - 提取元数据：标题、作者、页数
   - 计算 file_hash 用于去重
  ↓
2. 版面解析（layout）
   - 用 PyMuPDF / pdfplumber 提取每一页：
     * 文本块 + 字体 + 坐标
     * 图片 + 坐标
     * 表格
   - 识别页码（页脚 / 页眉）
  ↓
3. 目录识别
   - 优先从 PDF 书签（outline）提取
   - 失败则用第一页/前两页的目录文本
   - 解析为 (chapter_id, title, page_start, page_end) 列表
  ↓
4. 章节切分
   - 按目录的页码范围切分每一章
   - 章内进一步按二级标题切分 section
  ↓
5. 块分类
   - 通过字体大小、加粗、关键词识别 block_type
   - "例 X"、"例题 X" → example
   - "练习"、"习题" → exercise
   - "思考"、"探究" → concept
   - "小结"、"本章要点" → summary
  ↓
6. 公式与图表
   - 公式：保留 LaTeX（如 PyMuPDF 不支持，则 OCR）
   - 图表：截屏 + OCR 提取说明文字
  ↓
7. 知识点抽取（粗粒度）
   - 提取粗粒度 concept 名（不抽关系，关系留给 knowledge-graph-builder）
  ↓
8. 索引与存储
   - 写 PostgreSQL: `textbooks` + `textbook_blocks`
   - 写 pgvector: 每 block 一条 embedding
   - 写 MinIO: 原 PDF、章节图片
   - 写 `textbook_manifest.json` 到存储
```

## 实现要点

```python
# scripts/ingest_textbooks.py 核心伪代码
def ingest(pdf_path, subject, grade, version):
    manifest = {
        "textbook_id": make_id(subject, grade, version),
        "title": extract_title(pdf_path),
        ...
    }
    doc = fitz.open(pdf_path)
    chapters = extract_outline(doc)  # 书签 / 目录
    for ch in chapters:
        sections = split_sections(doc, ch)
        for sec in sections:
            blocks = classify_blocks(doc, sec)
            persist_blocks(blocks)  # -> postgres + vector
            embed_blocks(blocks)     # -> pgvector
    save_manifest(manifest)
    return manifest
```

## 质量标准

| 维度 | 标准 |
|---|---|
| 页码定位准确率 | ≥ 99%（核心考核） |
| 章节识别准确率 | ≥ 95% |
| block_type 分类 | ≥ 90% |
| 向量检索召回 | ≥ 85%（配合目录双检索） |
| 端到端耗时 | 100 页 PDF ≤ 3 分钟 |
| 大文件 | 500 页 ≤ 15 分钟 |

## 错误处理

| 错误 | 处理 |
|---|---|
| PDF 加密 | 提示用户提供密码或解密版本 |
| 没有书签 / 目录 | 降级为基于字体 + 标题规则识别 |
| 扫描版（无文本层） | 走 OCR：paddleocr / tesseract |
| 含双语混排 | 提示用户选主要语言 |
| 公式密集 | 调用 pix2tex / Nougat 单独处理公式页 |

## 护栏（必须强制）

1. **页码依据**：所有输出必须带 page_number，没有 page 依据的 block 标记 `unsourced=true`
2. **不编造**：识别不到的概念宁可不抽，不猜
3. **去重**：同一教材重复上传时基于 file_hash 跳过
4. **隐私**：日志中不打印学生作业图片内容，只记录 hash

## 输出引用格式

被后续 skill 引用时，统一格式：

```
《{title}》{version}，第 {chapter} 章 {section} 节，第 {page} 页
```

例如：`《数学 七年级 上册》人教版，第 1 章第 1 节，第 2 页`

## 不要做的事

- 不要试图"理解"教材内容做教学化解释（这是 pedagogy-method 的事）
- 不要直接生成知识图谱（这是 knowledge-graph-builder 的事）
- 不要替用户判断哪个版本更权威（让用户选）
- 不要把扫描失败的页悄悄跳过，必须在 manifest 中标记 `failed_pages`

## 依赖

- PyMuPDF / pdfplumber
- paddleocr（中英文混排）
- pix2tex（公式）
- sentence-transformers（embeddings，模型：shibing624/text2vec-base-chinese）
- PostgreSQL + pgvector
- MinIO / S3
