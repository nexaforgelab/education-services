"""
教材服务：入库、查询

严格模式：所有调用必须使用真实服务。
"""
import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker

logger = logging.getLogger(__name__)

# 把仓库根加入 sys.path 以调用 scripts
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


class TextbookService:
    """教材服务封装 — 真实数据库操作"""

    async def ingest(
        self,
        pdf_path: str,
        subject: str,
        grade: str,
        version: str,
        output_dir: str = "./out/",
        db_url: Optional[str] = None,
    ) -> dict:
        """
        解析教材 PDF 并写入数据库
        严格模式：必须真实执行 ingest_textbooks.py
        """
        # 严格检查依赖
        try:
            import fitz  # PyMuPDF
        except ImportError as e:
            raise RuntimeError(
                "PyMuPDF not installed. Run: pip install pymupdf --break-system-packages"
            ) from e

        # 调用真实的 ingest_textbooks.py
        from scripts.ingest_textbooks import ingest as ingest_pdf

        manifest = await asyncio.to_thread(
            ingest_pdf,
            pdf_path=pdf_path,
            subject=subject,
            grade=grade,
            version=version,
            output_dir=output_dir,
            db_url=db_url,
        )

        # 持久化到数据库
        if async_session_maker is None:
            raise RuntimeError("Database not configured")

        async with async_session_maker() as session:
            await session.execute(
                text("""
                INSERT INTO textbooks (id, subject, grade, version, title, publisher, file_hash, total_pages)
                VALUES (:id, :subject, :grade, :version, :title, :publisher, :file_hash, :total_pages)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    updated_at = NOW()
                """),
                {
                    "id": manifest["textbook_id"],
                    "subject": manifest["subject"],
                    "grade": manifest["grade"],
                    "version": manifest["version"],
                    "title": manifest["title"],
                    "publisher": manifest.get("publisher", ""),
                    "file_hash": manifest.get("file_hash", ""),
                    "total_pages": manifest.get("total_pages", 0),
                }
            )
            await session.commit()

        return {
            "textbook_id": manifest["textbook_id"],
            "title": manifest["title"],
            "total_pages": manifest["total_pages"],
            "chapters_count": len(manifest.get("chapters", [])),
            "manifest_url": f"{output_dir.rstrip('/')}/textbook_manifest.json",
        }

    async def list_textbooks(
        self, subject: Optional[str] = None, grade: Optional[str] = None
    ) -> List[dict]:
        """列出已入库教材 — 真实数据库查询"""
        if async_session_maker is None:
            raise RuntimeError("Database not configured")

        async with async_session_maker() as session:
            query = "SELECT id, subject, grade, version, title, publisher, total_pages, created_at FROM textbooks WHERE 1=1"
            params = {}
            if subject:
                query += " AND subject = :subject"
                params["subject"] = subject
            if grade:
                query += " AND grade = :grade"
                params["grade"] = grade
            query += " ORDER BY created_at DESC"

            result = await session.execute(text(query), params)
            rows = result.fetchall()
            return [
                {
                    "textbook_id": r[0],
                    "subject": r[1],
                    "grade": r[2],
                    "version": r[3],
                    "title": r[4],
                    "publisher": r[5],
                    "total_pages": r[6],
                    "created_at": r[7].isoformat() if r[7] else None,
                }
                for r in rows
            ]

    async def get_manifest(self, textbook_id: str) -> dict:
        """获取教材 manifest — 真实数据库查询"""
        if async_session_maker is None:
            raise RuntimeError("Database not configured")

        async with async_session_maker() as session:
            # 1. 查教材基本信息
            result = await session.execute(
                text("SELECT id, subject, grade, version, title, publisher, file_hash, total_pages FROM textbooks WHERE id = :id"),
                {"id": textbook_id}
            )
            row = result.fetchone()
            if not row:
                raise FileNotFoundError(f"Textbook {textbook_id} not found")

            # 2. 查 manifest 文件（从 out/ 目录）
            manifest_paths = [
                Path("./out") / textbook_id / "textbook_manifest.json",
                Path("./out") / "textbook_manifest.json",
            ]
            manifest = None
            for p in manifest_paths:
                if p.exists():
                    manifest = json.loads(p.read_text(encoding="utf-8"))
                    break

            if manifest:
                return manifest

            # 3. 数据库无 manifest，从 out 目录重建
            return {
                "textbook_id": row[0],
                "subject": row[1],
                "grade": row[2],
                "version": row[3],
                "title": row[4],
                "publisher": row[5],
                "file_hash": row[6],
                "total_pages": row[7],
                "chapters": [],
            }

    async def get_chapter_content(self, textbook_id: str, chapter_id: str) -> dict:
        """获取章节内容 — 真实数据库查询"""
        if async_session_maker is None:
            raise RuntimeError("Database not configured")

        async with async_session_maker() as session:
            result = await session.execute(
                text("""
                SELECT id, chapter_id, section_id, page_number, block_type, content, bbox, image_url, metadata
                FROM textbook_blocks
                WHERE textbook_id = :textbook_id AND chapter_id = :chapter_id
                ORDER BY page_number, id
                """),
                {"textbook_id": textbook_id, "chapter_id": chapter_id}
            )
            rows = result.fetchall()
            blocks = [
                {
                    "id": str(r[0]),
                    "chapter_id": r[1],
                    "section_id": r[2],
                    "page_number": r[3],
                    "block_type": r[4],
                    "content": r[5],
                    "bbox": r[6],
                    "image_url": r[7],
                    "metadata": r[8] or {},
                }
                for r in rows
            ]
            return {
                "textbook_id": textbook_id,
                "chapter_id": chapter_id,
                "blocks": blocks,
                "block_count": len(blocks),
            }
