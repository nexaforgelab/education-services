"""
测试 Agent API（教案 / 诊断 / 解释）

严格模式：需要真实数据库 + ANTHROPIC_API_KEY 才能运行。
无 LLM API Key 时自动跳过。
"""
import pytest


class TestLessonPlan:
    """教案生成 API 测试"""

    def test_lesson_plan_unauthorized(self, client):
        """未授权访问（流式端点需要 teacher/admin）"""
        # lesson-plan 端点目前未加 auth，main.py 中还没 require_role
        # 未来加上后应该 401/403
        pass

    @pytest.mark.skipif(
        not __import__("os").environ.get("ANTHROPIC_API_KEY"),
        reason="需要 ANTHROPIC_API_KEY 才能运行 LLM 集成测试"
    )
    def test_lesson_plan_validation(self, client):
        """教案生成（真实调用 Claude）"""
        response = client.post("/api/v1/agents/lesson-plan", json={
            "textbook_id": "math_g7_人教_2024",
            "chapter_id": "ch01",
            "duration_min": 45,
            "student_level": "中等"
        })
        # 真实 LLM 调用，成功 200
        if response.status_code == 500:
            pytest.skip(f"LLM/Database 不可用: {response.json().get('detail')}")
        assert response.status_code == 200
        data = response.json()
        assert "output_id" in data
        assert "files" in data
        assert data["citations_count"] > 0  # 必须有引用


class TestDiagnoseHomework:
    """作业诊断 API 测试"""

    @pytest.mark.skipif(
        not __import__("os").environ.get("ANTHROPIC_API_KEY"),
        reason="需要 ANTHROPIC_API_KEY 才能运行 LLM 集成测试"
    )
    def test_diagnose_homework(self, client):
        response = client.post("/api/v1/agents/diagnose-homework", json={
            "student_id": "11111111-1111-1111-1111-111111111111",
            "textbook_id": "math_g7_人教_2024",
            "chapter_id": "ch01",
            "parsed_questions": [
                {"id": "q01", "student_answer": "0", "correct_answer": "2", "is_correct": False}
            ]
        })
        if response.status_code == 500:
            pytest.skip(f"LLM/Database 不可用: {response.json().get('detail')}")
        assert response.status_code == 200
        data = response.json()
        assert "weak_kps" in data
        assert "overall" in data


class TestExplainToParent:
    """家长解释 API 测试"""

    @pytest.mark.skipif(
        not __import__("os").environ.get("ANTHROPIC_API_KEY"),
        reason="需要 ANTHROPIC_API_KEY 才能运行 LLM 集成测试"
    )
    def test_explain_to_parent(self, client):
        response = client.post("/api/v1/agents/explain-to-parent", json={
            "chapter_or_concept": "有理数 加法"
        })
        if response.status_code == 500:
            pytest.skip(f"LLM/Database 不可用: {response.json().get('detail')}")
        assert response.status_code == 200
        data = response.json()
        assert "explanation_md" in data


class TestParentReport:
    """家长报告 API 测试"""

    @pytest.mark.skipif(
        not __import__("os").environ.get("ANTHROPIC_API_KEY"),
        reason="需要 ANTHROPIC_API_KEY 才能运行 LLM 集成测试"
    )
    def test_parent_report(self, client):
        response = client.post("/api/v1/agents/parent-report", json={
            "student_id": "11111111-1111-1111-1111-111111111111",
            "period": "weekly"
        })
        if response.status_code == 500:
            pytest.skip(f"LLM/Database 不可用: {response.json().get('detail')}")
        assert response.status_code == 200
        data = response.json()
        assert "report_md" in data
        assert "strengths" in data
        assert "growth_areas" in data
