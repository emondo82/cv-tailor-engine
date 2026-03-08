from __future__ import annotations

import os
from dotenv import load_dotenv

from llm_resume_enhancer_openai import enhance_resume_with_openai
from llm_resume_enhancer_gemini import enhance_resume_with_gemini

load_dotenv()

USE_LLM_RESUME_ENHANCER = os.getenv("USE_LLM_RESUME_ENHANCER", "false").lower() == "true"


def enhance_resume_versions(
    resume_markdown: str,
    job_title: str,
    jd_skills: list[str],
    company_style: str = "general",
) -> dict:
    if not USE_LLM_RESUME_ENHANCER:
        return {
            "base": resume_markdown,
            "openai": resume_markdown,
            "gemini": resume_markdown,
        }

    openai_version = enhance_resume_with_openai(
        resume_markdown=resume_markdown,
        job_title=job_title,
        jd_skills=jd_skills,
        company_style=company_style,
    )

    gemini_version = enhance_resume_with_gemini(
        resume_markdown=resume_markdown,
        job_title=job_title,
        jd_skills=jd_skills,
        company_style=company_style,
    )

    return {
        "base": resume_markdown,
        "openai": openai_version,
        "gemini": gemini_version,
    }