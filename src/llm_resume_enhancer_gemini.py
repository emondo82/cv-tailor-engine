from __future__ import annotations

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"


def enhance_resume_with_gemini(
    resume_markdown: str,
    job_title: str,
    jd_skills: list[str],
    company_style: str = "general",
) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    text = (response.text or "").strip()
    return text or resume_markdown