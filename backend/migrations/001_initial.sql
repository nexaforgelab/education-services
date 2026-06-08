-- Education Services — 数据库 schema
-- 适用于 PostgreSQL 15+ with pgvector extension

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============== 教材 ==============

CREATE TABLE IF NOT EXISTS textbooks (
    id              TEXT PRIMARY KEY,         -- math_g7_vol1_pep_2024
    subject         TEXT NOT NULL,            -- math, english, chinese...
    grade           TEXT NOT NULL,            -- "7"
    version         TEXT NOT NULL,            -- 人教版
    title           TEXT NOT NULL,
    publisher       TEXT,
    file_url        TEXT,                     -- MinIO/S3 URL
    file_hash       TEXT,                     -- sha256:...
    total_pages     INTEGER,
    edition_year    INTEGER,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_textbooks_subject_grade ON textbooks(subject, grade);
CREATE INDEX idx_textbooks_version ON textbooks(version);


-- ============== 教材内容块 ==============

CREATE TABLE IF NOT EXISTS textbook_blocks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    textbook_id     TEXT NOT NULL REFERENCES textbooks(id) ON DELETE CASCADE,
    chapter_id      TEXT NOT NULL,
    section_id      TEXT,
    page_number     INTEGER NOT NULL,
    block_type      TEXT NOT NULL,            -- concept | example | exercise | image | table | summary | definition
    content         TEXT NOT NULL,
    bbox            JSONB,                    -- [x0, y0, x1, y1]
    image_url       TEXT,
    embedding       vector(768),              -- sentence-transformers 输出
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_textbook_blocks_textbook ON textbook_blocks(textbook_id);
CREATE INDEX idx_textbook_blocks_chapter ON textbook_blocks(textbook_id, chapter_id);
CREATE INDEX idx_textbook_blocks_section ON textbook_blocks(textbook_id, section_id);
CREATE INDEX idx_textbook_blocks_page ON textbook_blocks(textbook_id, page_number);
CREATE INDEX idx_textbook_blocks_type ON textbook_blocks(block_type);

-- 向量索引
CREATE INDEX idx_textbook_blocks_embedding ON textbook_blocks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- ============== 知识点 ==============

CREATE TABLE IF NOT EXISTS knowledge_points (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    textbook_id     TEXT REFERENCES textbooks(id) ON DELETE CASCADE,
    subject         TEXT NOT NULL,
    grade           TEXT NOT NULL,
    chapter_id      TEXT,
    name            TEXT NOT NULL,
    description     TEXT,
    difficulty      TEXT,                     -- easy | medium | hard
    prerequisites   UUID[] DEFAULT '{}',      -- 关联前置知识点
    curriculum_std  TEXT,                     -- 课程标准依据
    common_misconceptions JSONB DEFAULT '[]'::jsonb,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kp_subject_grade ON knowledge_points(subject, grade);
CREATE INDEX idx_kp_textbook ON knowledge_points(textbook_id);
CREATE INDEX idx_kp_chapter ON knowledge_points(chapter_id);


-- ============== 学生画像 ==============

CREATE TABLE IF NOT EXISTS student_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_alias      TEXT NOT NULL,            -- 别名，不写真名
    grade           TEXT,
    school_type     TEXT,                     -- public | private | homeschool
    subjects        JSONB DEFAULT '{}'::jsonb,  -- {math: {level, strengths, weaknesses, mastery_map}}
    learning_notes  TEXT,
    motivation      JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_student_profiles_grade ON student_profiles(grade);


-- ============== 作业 ==============

CREATE TABLE IF NOT EXISTS homework_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
    textbook_id     TEXT REFERENCES textbooks(id),
    chapter_id      TEXT,
    raw_answer_url  TEXT,                     -- MinIO/S3 URL
    parsed_data     JSONB,                    -- OCR 后的题目+答案
    diagnosis_json  JSONB,                    -- 诊断结果
    status          TEXT DEFAULT 'pending',   -- pending | diagnosed | reviewed
    submitted_at    TIMESTAMPTZ DEFAULT NOW(),
    diagnosed_at    TIMESTAMPTZ
);

CREATE INDEX idx_homework_student ON homework_records(student_id);
CREATE INDEX idx_homework_chapter ON homework_records(chapter_id);
CREATE INDEX idx_homework_status ON homework_records(status);


-- ============== 学习事件 ==============

CREATE TABLE IF NOT EXISTS learning_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
    event_type      TEXT NOT NULL,            -- homework_submit | unit_test | review_done
    chapter_id      TEXT,
    knowledge_point_id UUID REFERENCES knowledge_points(id),
    mastery_delta   REAL,                     -- -1.0 ~ 1.0
    notes           TEXT,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_learning_events_student ON learning_events(student_id);
CREATE INDEX idx_learning_events_kp ON learning_events(knowledge_point_id);


-- ============== Agent 输出归档 ==============

CREATE TABLE IF NOT EXISTS agent_outputs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name      TEXT NOT NULL,
    command         TEXT NOT NULL,            -- /lesson-plan, /diagnose-homework
    user_role       TEXT,                     -- teacher | parent
    user_id         UUID,
    chapter_id      TEXT,
    textbook_id     TEXT REFERENCES textbooks(id),
    input_params    JSONB,
    output_files    JSONB,                    -- 指向 ./out/ 的文件
    safety_flags    JSONB DEFAULT '[]'::jsonb,
    reviewed_by_human BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_outputs_agent ON agent_outputs(agent_name);
CREATE INDEX idx_agent_outputs_chapter ON agent_outputs(chapter_id);
CREATE INDEX idx_agent_outputs_created ON agent_outputs(created_at);


-- ============== 引用追溯 ==============

CREATE TABLE IF NOT EXISTS citations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    output_id       UUID REFERENCES agent_outputs(id) ON DELETE CASCADE,
    textbook_id     TEXT REFERENCES textbooks(id),
    chapter_id      TEXT,
    section_id      TEXT,
    page_number     INTEGER,
    block_id        UUID REFERENCES textbook_blocks(id),
    quote           TEXT,                     -- 引用原文
    confidence      TEXT,                     -- textbook_original | textbook_derived | curriculum_standard | general
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_citations_output ON citations(output_id);
CREATE INDEX idx_citations_textbook ON citations(textbook_id);


-- ============== 更新时间戳触发器 ==============

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_textbooks_updated_at
    BEFORE UPDATE ON textbooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_student_profiles_updated_at
    BEFORE UPDATE ON student_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
