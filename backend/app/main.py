"""
Education Services — FastAPI 主应用

提供 RESTful API 给前端 / SDK / Cowork 插件调用。
"""
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import get_db, init_db
from app.services.textbook import TextbookService
from app.services.agent import AgentService
from app.api import auth, streaming, websocket

configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info("Starting Education Services backend", env=settings.env)
    await init_db()
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Education Services API",
    description="教材驱动的教师/家长辅导 Agent 后端",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(streaming.router, prefix="/api/v1/agents", tags=["streaming"])
app.include_router(websocket.router, tags=["websocket"])


# ============ Health ============

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.env}


# ============ Schemas ============

class IngestTextbookRequest(BaseModel):
    pdf_path: str
    subject: str
    grade: str
    version: str


class IngestTextbookResponse(BaseModel):
    textbook_id: str
    title: str
    total_pages: int
    chapters_count: int
    manifest_url: str


class LessonPlanRequest(BaseModel):
    textbook_id: str
    chapter_id: str
    duration_min: int = Field(45, ge=15, le=180)
    student_level: str = "中等"  # 基础薄弱 | 中等 | 拔高


class LessonPlanResponse(BaseModel):
    output_id: str
    output_dir: str
    files: List[str]
    citations_count: int


class DiagnoseHomeworkRequest(BaseModel):
    student_id: str
    textbook_id: str
    chapter_id: str
    homework_file_url: Optional[str] = None
    parsed_questions: Optional[List[dict]] = None


class DiagnoseHomeworkResponse(BaseModel):
    output_id: str
    overall: dict
    items: List[dict]
    weak_kps: List[str]


class ExplainToParentRequest(BaseModel):
    chapter_or_concept: str
    textbook_id: Optional[str] = None


class ExplainToParentResponse(BaseModel):
    output_id: str
    explanation_md: str
    parent_coaching_script: str
    ten_min_practice: str


class ParentReportRequest(BaseModel):
    student_id: str
    period: str = "weekly"  # weekly | monthly | unit


class ParentReportResponse(BaseModel):
    output_id: str
    report_md: str
    strengths: List[str]
    growth_areas: List[str]


# ============ API Endpoints ============

@app.post("/api/v1/textbooks/ingest", response_model=IngestTextbookResponse)
async def ingest_textbook(req: IngestTextbookRequest):
    """解析教材 PDF 并入库"""
    svc = TextbookService()
    try:
        result = await svc.ingest(
            pdf_path=req.pdf_path,
            subject=req.subject,
            grade=req.grade,
            version=req.version,
        )
        return IngestTextbookResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("ingest_textbook failed", error=str(e))
        raise HTTPException(status_code=500, detail="Ingest failed")


@app.post("/api/v1/agents/lesson-plan", response_model=LessonPlanResponse)
async def lesson_plan(req: LessonPlanRequest):
    """生成教案"""
    svc = AgentService()
    result = await svc.run_lesson_plan(
        textbook_id=req.textbook_id,
        chapter_id=req.chapter_id,
        duration_min=req.duration_min,
        student_level=req.student_level,
        user_role="teacher",
    )
    return LessonPlanResponse(**result)


@app.post("/api/v1/agents/diagnose-homework", response_model=DiagnoseHomeworkResponse)
async def diagnose_homework(req: DiagnoseHomeworkRequest):
    """作业诊断"""
    svc = AgentService()
    result = await svc.run_diagnose_homework(
        student_id=req.student_id,
        textbook_id=req.textbook_id,
        chapter_id=req.chapter_id,
        homework_file_url=req.homework_file_url,
        parsed_questions=req.parsed_questions,
    )
    return DiagnoseHomeworkResponse(**result)


@app.post("/api/v1/agents/explain-to-parent", response_model=ExplainToParentResponse)
async def explain_to_parent(req: ExplainToParentRequest):
    """家长版解释"""
    svc = AgentService()
    result = await svc.run_explain_to_parent(
        chapter_or_concept=req.chapter_or_concept,
        textbook_id=req.textbook_id,
    )
    return ExplainToParentResponse(**result)


@app.post("/api/v1/agents/parent-report", response_model=ParentReportResponse)
async def parent_report(req: ParentReportRequest):
    """家长沟通报告"""
    svc = AgentService()
    result = await svc.run_parent_report(
        student_id=req.student_id,
        period=req.period,
    )
    return ParentReportResponse(**result)


# ============ 教材查询 ============

@app.get("/api/v1/textbooks")
async def list_textbooks(subject: Optional[str] = None, grade: Optional[str] = None):
    """列出已入库教材"""
    svc = TextbookService()
    return await svc.list_textbooks(subject=subject, grade=grade)


@app.get("/api/v1/textbooks/{textbook_id}/manifest")
async def get_textbook_manifest(textbook_id: str):
    """获取教材 manifest"""
    svc = TextbookService()
    return await svc.get_manifest(textbook_id)


@app.get("/api/v1/textbooks/{textbook_id}/chapters/{chapter_id}/content")
async def get_chapter_content(textbook_id: str, chapter_id: str):
    """获取章节内容"""
    svc = TextbookService()
    return await svc.get_chapter_content(textbook_id, chapter_id)
