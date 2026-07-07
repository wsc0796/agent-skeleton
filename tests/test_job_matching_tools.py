from src.tools.business.job_matching.tools import (
    analyze_jd,
    generate_gap_report,
    generate_study_plan,
    match_resume,
)

SAMPLE_JD = """
AI Agent实习生
要求：Python, LLM, RAG, Agent开发经验
熟悉 FastAPI, Docker, Git
加分：LangChain, 大模型应用, React
"""


class TestJobMatchingTools:
    def test_analyze_jd_extracts_skills(self):
        result = analyze_jd(SAMPLE_JD)
        assert result["job_type"] == "ai_agent"
        assert "Python" in result["required_skills"]
        assert "LLM" in result["required_skills"]
        assert "RAG" in result["required_skills"]
        assert "Agent" in result["required_skills"]
        assert "Docker" in result["required_skills"]

    def test_analyze_jd_empty_text(self):
        result = analyze_jd("")
        assert result["job_type"] == "other"
        assert result["required_skills"] == []

    def test_match_resume_good_match(self):
        result = match_resume(
            resume_skills=["Python", "FastAPI", "Docker", "Git", "LLM", "RAG"],
            jd_text=SAMPLE_JD,
        )
        assert result["match_score"] >= 60
        assert "Python" in result["matched_skills"]

    def test_match_resume_poor_match(self):
        result = match_resume(
            resume_skills=["Java", "Spring"],
            jd_text=SAMPLE_JD,
        )
        assert result["match_score"] < 30

    def test_generate_gap_report(self):
        result = generate_gap_report(
            matched=["Python", "Git"],
            missing=["LLM", "RAG", "Agent", "Docker"],
            job_type="ai_agent",
        )
        assert result["coverage_pct"] == 33  # 2/6
        assert len(result["priority_actions"]) == 4

    def test_generate_study_plan(self):
        result = generate_study_plan(
            missing_skills=["LLM", "RAG", "Agent", "Docker", "React"],
            weeks=3,
        )
        assert result["timeframe_weeks"] == 3
        assert result["total_skills"] == 5
        assert "week_1" in result["weekly_plan"]
