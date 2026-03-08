from __future__ import annotations

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-5-mini"


def enhance_resume_with_openai(
    resume_markdown: str,
    job_title: str,
    jd_skills: list[str],
    company_style: str = "general",
) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are improving a tailored resume for a specific job application.

Your task:
Rewrite the resume for stronger clarity, professional tone, and ATS alignment.

Rules:
- Preserve all factual meaning.
- Do not invent achievements, metrics, tools, systems, certifications, or responsibilities.
- Do not add experience that is not already present.
- Keep the same section structure and order.
- Improve phrasing, grammar, readability, and keyword alignment to the target role.
- Keep the writing concise and credible.
- Return only the rewritten resume in plain markdown.

Target role:
{job_title}

Important JD skills:
{", ".join(jd_skills[:10])}

Company style:
{company_style}

Resume markdown:
{resume_markdown}
""".strip()

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
    )

    text = getattr(response, "output_text", "").strip()
    return text or resume_markdown