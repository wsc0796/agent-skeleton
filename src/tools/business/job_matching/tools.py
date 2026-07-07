"""Job matching business tools — the "customize per JD" showcase.

Replace or extend these when targeting a specific company's job description.
"""


from pydantic import BaseModel, Field

from src.core.tool_registry import ToolSpec

# ── Skill rule engine (same pattern as internship-tracker-api) ──

SKILL_KEYWORDS: dict[str, list[str]] = {
    "Python": ["python", "fastapi", "flask", "django"],
    "Java": ["java", "spring", "mybatis", "hibernate"],
    "JavaScript": ["javascript", "js", "typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Vue": ["vue", "vue.js", "vuejs"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite"],
    "Redis": ["redis", "cache"],
    "Docker": ["docker", "container"],
    "Git": ["git", "github", "gitlab"],
    "Linux": ["linux", "unix", "bash", "shell"],
    "LLM": ["llm", "大模型", "openai", "deepseek", "langchain"],
    "RAG": ["rag", "检索增强", "retrieval"],
    "Agent": ["agent", "智能体", "multi-agent", "react", "function calling"],
    "pytest": ["pytest", "测试", "test automation", "单元测试"],
    "CI/CD": ["ci/cd", "github actions", "jenkins", "pipeline"],
}

JOB_TYPE_KEYWORDS: dict[str, list[str]] = {
    "ai_agent": ["agent", "llm", "大模型", "rag", "智能体", "prompt", "langchain"],
    "java_backend": ["java", "spring", "mybatis", "mysql", "后端"],
    "fullstack": ["react", "vue", "typescript", "全栈", "前后端"],
    "test_dev": ["测试", "pytest", "自动化测试", "质量", "qa"],
}


class AnalyzeJDArgs(BaseModel):
    jd_text: str = Field(..., min_length=1, description="Full job description text")


class MatchResumeArgs(BaseModel):
    resume_skills: list[str] = Field(..., min_length=1, description="Your skills list")
    jd_text: str = Field(..., min_length=1, description="Job description text")


class GenerateGapReportArgs(BaseModel):
    matched: list[str] = Field(default_factory=list, description="Matched skills")
    missing: list[str] = Field(default_factory=list, description="Missing skills")
    job_type: str = Field(default="unknown", description="Job type classification")


class GenerateStudyPlanArgs(BaseModel):
    missing_skills: list[str] = Field(..., min_length=1, description="Skills to learn")
    weeks: int = Field(default=4, description="Study timeframe in weeks")


# ── Tool implementations ──

def analyze_jd(jd_text: str) -> dict:
    """Extract required skills and classify job type from JD text."""
    text_lower = jd_text.lower()

    required: list[str] = []
    for skill, keywords in SKILL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            required.append(skill)

    job_type = "other"
    type_scores: dict[str, int] = {}
    for jt, keywords in JOB_TYPE_KEYWORDS.items():
        type_scores[jt] = sum(1 for kw in keywords if kw in text_lower)
    if type_scores and max(type_scores.values()) > 0:
        job_type = max(type_scores, key=type_scores.get)

    return {
        "job_type": job_type,
        "required_skills": required,
        "skill_count": len(required),
    }


def match_resume(resume_skills: list[str], jd_text: str) -> dict:
    """Match resume skills against JD requirements."""
    jd_analysis = analyze_jd(jd_text)
    my_skills = set(s.lower() for s in resume_skills)

    matched = [s for s in jd_analysis["required_skills"] if s.lower() in my_skills]
    missing = [s for s in jd_analysis["required_skills"] if s.lower() not in my_skills]

    score = round(len(matched) / max(len(jd_analysis["required_skills"]), 1) * 100)

    return {
        "job_type": jd_analysis["job_type"],
        "required_skills": jd_analysis["required_skills"],
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": score,
    }


def generate_gap_report(
    matched: list[str],
    missing: list[str],
    job_type: str = "unknown",
) -> dict:
    """Generate a structured skill gap report."""
    total = len(matched) + len(missing)
    coverage = round(len(matched) / max(total, 1) * 100)

    actions: list[str] = []
    for skill in missing[:5]:
        actions.append(
            f"Learn {skill}: build a minimal project (API + tests + README) "
            f"demonstrating {skill} in a real scenario."
        )

    return {
        "coverage_pct": coverage,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "job_type": job_type,
        "priority_actions": actions,
        "summary": (
            f"You have {coverage}% skill coverage for this {job_type} role. "
            f"Focus on: {', '.join(missing[:3])}."
        ),
    }


def generate_study_plan(missing_skills: list[str], weeks: int = 4) -> dict:
    """Generate a week-by-week study plan for missing skills."""
    skills_per_week = max(1, len(missing_skills) // max(weeks, 1))

    plan: dict[str, list[str]] = {}
    for w in range(1, weeks + 1):
        start = (w - 1) * skills_per_week
        end = start + skills_per_week
        week_skills = missing_skills[start:end]
        plan[f"week_{w}"] = week_skills

    return {
        "timeframe_weeks": weeks,
        "total_skills": len(missing_skills),
        "weekly_plan": plan,
        "advice": "Each week: 1) learn concepts, 2) build a mini-project, 3) write tests, 4) push to GitHub.",
    }


def tools() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="analyze_jd",
            description="Analyze a job description to extract required skills and classify the job type (ai_agent, java_backend, fullstack, test_dev, other).",
            args_model=AnalyzeJDArgs,
            function=analyze_jd,
            category="business",
        ),
        ToolSpec(
            name="match_resume",
            description="Match your resume skills against a JD. Returns matched skills, missing skills, and a match score (0-100).",
            args_model=MatchResumeArgs,
            function=match_resume,
            category="business",
        ),
        ToolSpec(
            name="generate_gap_report",
            description="Generate a detailed skill gap report with priority actions for closing the gaps.",
            args_model=GenerateGapReportArgs,
            function=generate_gap_report,
            category="business",
        ),
        ToolSpec(
            name="generate_study_plan",
            description="Create a week-by-week study plan to learn missing skills within a given timeframe.",
            args_model=GenerateStudyPlanArgs,
            function=generate_study_plan,
            category="business",
        ),
    ]
