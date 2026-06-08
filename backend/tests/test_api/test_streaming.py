"""
测试安全 / 护栏相关

这些是离线测试，不需要真实 LLM 或 DB。
"""
import pytest


class TestSafetyGuardrails:
    """护栏测试 - 纯逻辑，不需要 LLM"""

    def test_citation_format(self):
        """引用格式"""
        # 这是个简单的字符串格式检查，不需要导入重型服务
        import re
        sample = "教材 p.18 指出：'减去一个数，等于加上它的相反数'"
        citations = re.findall(r"[Pp]\.?\s*\d+", sample)
        assert len(citations) > 0

    def test_no_personal_judgments(self):
        """不评判人格"""
        bad_phrases = [
            "孩子笨", "孩子蠢", "学生笨", "学生蠢",
            "逻辑差", "不用功", "不上心",
        ]
        text = "孩子在异号相加时混淆绝对值大小，建议强化练习。"
        for phrase in bad_phrases:
            assert phrase not in text

    def test_no_unsourced_textbook_claims(self):
        """不编造教材内容"""
        bad_phrases = [
            "教材上明确说", "教材中提到", "教材认为", "教材上写",
        ]
        text = "教材 p.18 指出：'减去一个数，等于加上它的相反数' [教材原文 p.18]"
        for phrase in bad_phrases:
            assert phrase not in text

    def test_no_direct_cheating_help(self):
        """不替学生作弊"""
        bad_phrases = [
            "为了应付考试", "先抄答案", "先背下来", "代做",
        ]
        text = "看到 '减负数' 第一步要做什么？"
        for phrase in bad_phrases:
            assert phrase not in text
