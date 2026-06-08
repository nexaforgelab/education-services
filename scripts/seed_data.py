#!/usr/bin/env python3
"""
seed_data.py — 灌入种子数据

为开发/演示环境创建一些示例数据：
  - 2-3 个示例学生画像
  - 示例作业记录
  - 示例学习事件
  - 演示用教师/家长账号

用法:
  python scripts/seed_data.py
  python scripts/seed_data.py --reset  # 先清空
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
except ImportError:
    print("Error: pip install sqlalchemy asyncpg --break-system-packages", file=sys.stderr)
    sys.exit(1)


# 加载 .env
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def get_db_url() -> str:
    load_env()
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("Error: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return db_url


# 种子数据
SAMPLE_STUDENTS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name_alias": "小明",
        "grade": "7",
        "school_type": "public",
        "subjects": {
            "math": {
                "level": "中等",
                "strengths": ["正负数判定", "基础运算"],
                "weaknesses": ["有理数加减法符号法则", "一元一次方程应用题"],
                "mastery_map": {
                    "正负数判定": 0.85,
                    "有理数加减法": 0.45,
                    "一元一次方程": 0.30,
                }
            }
        },
        "learning_notes": "对应用题理解慢，需要更多生活化类比",
        "motivation": {"type": "外部驱动", "goal": "期末考试 85+"},
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "name_alias": "小红",
        "grade": "7",
        "school_type": "public",
        "subjects": {
            "math": {
                "level": "拔高",
                "strengths": ["几何直观", "代数变形"],
                "weaknesses": ["计算速度"],
                "mastery_map": {
                    "有理数运算": 0.92,
                    "一元一次方程": 0.88,
                }
            }
        },
        "learning_notes": "理解快，但需要更多练习提升熟练度",
        "motivation": {"type": "内部驱动", "goal": "数学竞赛"},
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "name_alias": "小华",
        "grade": "4",
        "school_type": "public",
        "subjects": {
            "math": {
                "level": "基础薄弱",
                "strengths": ["乘法口诀"],
                "weaknesses": ["分数概念", "应用题阅读"],
                "mastery_map": {
                    "加减法": 0.90,
                    "乘法": 0.70,
                    "分数": 0.30,
                }
            }
        },
        "learning_notes": "需要家长陪读，专注力短",
        "motivation": {"type": "外部驱动", "goal": "跟上课堂进度"},
    },
]

SAMPLE_KNOWLEDGE_POINTS = [
    {
        "subject": "math", "grade": "7", "chapter_id": "ch01",
        "name": "有理数", "description": "正数、负数、0 的统称",
        "difficulty": "easy",
        "common_misconceptions": ["负数比正数小", "0 不是有理数"],
    },
    {
        "subject": "math", "grade": "7", "chapter_id": "ch01",
        "name": "有理数加减法", "description": "同号相加取相同符号，异号相加取绝对值大者",
        "difficulty": "medium",
        "prerequisites": ["有理数"],
        "common_misconceptions": ["符号搞错", "绝对值运算错误"],
    },
    {
        "subject": "math", "grade": "7", "chapter_id": "ch02",
        "name": "一元一次方程", "description": "只含有一个未知数，且未知数次数为 1 的方程",
        "difficulty": "medium",
        "common_misconceptions": ["移项不变号", "系数化为 1 时忘记除以系数"],
    },
]


async def seed(reset: bool = False):
    db_url = get_db_url()
    print(f"🌱 灌入种子数据到: {db_url.split('@')[-1]}")

    engine = create_async_engine(db_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with Session() as session:
            if reset:
                print("⚠️  清空示例数据...")
                await session.execute(text("DELETE FROM learning_events WHERE metadata->>'seed' = 'true'"))
                await session.execute(text("DELETE FROM homework_records WHERE metadata->>'seed' = 'true'"))
                await session.execute(text("DELETE FROM student_profiles WHERE name_alias IN ('小明', '小红', '小华')"))
                await session.execute(text("DELETE FROM knowledge_points WHERE name IN ('有理数', '有理数加减法', '一元一次方程')"))
                await session.commit()
                print("   ✅ 已清空")

            # 1. 学生画像
            print("👨‍🎓 创建学生画像...")
            for s in SAMPLE_STUDENTS:
                await session.execute(
                    text("""
                    INSERT INTO student_profiles
                    (id, name_alias, grade, school_type, subjects, learning_notes, motivation, created_at, updated_at)
                    VALUES (:id, :name, :grade, :st, CAST(:subj AS JSONB), :notes, CAST(:mot AS JSONB), NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        name_alias = EXCLUDED.name_alias,
                        subjects = EXCLUDED.subjects,
                        updated_at = NOW()
                    """),
                    {
                        "id": s["id"],
                        "name": s["name_alias"],
                        "grade": s["grade"],
                        "st": s["school_type"],
                        "subj": json.dumps(s["subjects"], ensure_ascii=False),
                        "notes": s["learning_notes"],
                        "mot": json.dumps(s["motivation"], ensure_ascii=False),
                    }
                )
            await session.commit()
            print(f"   ✅ 创建 {len(SAMPLE_STUDENTS)} 个学生")

            # 2. 知识点
            print("📚 创建知识点...")
            for kp in SAMPLE_KNOWLEDGE_POINTS:
                await session.execute(
                    text("""
                    INSERT INTO knowledge_points
                    (subject, grade, chapter_id, name, description, difficulty, common_misconceptions)
                    VALUES (:s, :g, :c, :n, :d, :diff, CAST(:m AS JSONB))
                    """),
                    {
                        "s": kp["subject"],
                        "g": kp["grade"],
                        "c": kp["chapter_id"],
                        "n": kp["name"],
                        "d": kp["description"],
                        "diff": kp["difficulty"],
                        "m": json.dumps(kp["common_misconceptions"], ensure_ascii=False),
                    }
                )
            await session.commit()
            print(f"   ✅ 创建 {len(SAMPLE_KNOWLEDGE_POINTS)} 个知识点")

            # 3. 学习事件
            print("📊 创建学习事件...")
            events = [
                ("homework_submit", "ch01", 0.05, "完成有理数加减法作业，正确率 70%", "11111111-1111-1111-1111-111111111111"),
                ("unit_test", "ch01", -0.10, "有理数单元测试 65 分，符号法则失分多", "11111111-1111-1111-1111-111111111111"),
                ("review_done", "ch01", 0.15, "完成错题复习，符号法则正确率提升到 80%", "11111111-1111-1111-1111-111111111111"),
                ("homework_submit", "ch01", 0.20, "完成有理数拔高题，全部正确", "22222222-2222-2222-2222-222222222222"),
                ("homework_submit", "ch02", -0.20, "一元一次方程应用题不理解题意", "11111111-1111-1111-1111-111111111111"),
            ]
            for etype, chapter, delta, notes, sid in events:
                await session.execute(
                    text("""
                    INSERT INTO learning_events
                    (student_id, event_type, chapter_id, mastery_delta, notes, metadata, created_at)
                    VALUES (:sid, :et, :c, :d, :n, CAST(:m AS JSONB), :t)
                    """),
                    {
                        "sid": sid,
                        "et": etype,
                        "c": chapter,
                        "d": delta,
                        "n": notes,
                        "m": json.dumps({"seed": "true"}, ensure_ascii=False),
                        "t": datetime.utcnow() - timedelta(days=len(events) - events.index((etype, chapter, delta, notes, sid))),
                    }
                )
            await session.commit()
            print(f"   ✅ 创建 {len(events)} 个学习事件")

            # 4. 作业记录
            print("📝 创建作业记录...")
            homework_data = {
                "questions": [
                    {"id": "q1", "content": "(-3) + 5 = ?", "student_answer": "2", "correct_answer": "2", "is_correct": True},
                    {"id": "q2", "content": "(-3) + (-5) = ?", "student_answer": "-2", "correct_answer": "-8", "is_correct": False},
                    {"id": "q3", "content": "5 - (-3) = ?", "student_answer": "2", "correct_answer": "8", "is_correct": False},
                ],
                "submitted_at": datetime.utcnow().isoformat(),
            }
            await session.execute(
                text("""
                INSERT INTO homework_records
                (student_id, textbook_id, chapter_id, parsed_data, status, submitted_at, metadata)
                VALUES (:sid, :tid, :c, CAST(:pd AS JSONB), 'pending', NOW(), CAST(:m AS JSONB))
                """),
                {
                    "sid": "11111111-1111-1111-1111-111111111111",
                    "tid": "math_g7_人教_2024",
                    "c": "ch01",
                    "pd": json.dumps(homework_data, ensure_ascii=False),
                    "m": json.dumps({"seed": "true"}, ensure_ascii=False),
                }
            )
            await session.commit()
            print(f"   ✅ 创建 1 个作业记录")

        print("\n✅ 种子数据灌入完成！")
        print("\n📋 演示账号:")
        print("   小明 (grade 7, 基础中等)  - ID: 11111111-1111-1111-1111-111111111111")
        print("   小红 (grade 7, 拔高)      - ID: 22222222-2222-2222-2222-222222222222")
        print("   小华 (grade 4, 基础薄弱)  - ID: 33333333-3333-3333-3333-333333333333")

    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="先清空示例数据")
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset))


if __name__ == "__main__":
    main()
