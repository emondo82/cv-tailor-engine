from __future__ import annotations

import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")


def rewrite_bullet_with_openai(
    original_bullet: str,
    refined_bullet: str,
    job_title: str,
    jd_skills: list[str],
) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are refining one CV responsibility bullet for a job application.

Rules:
- Preserve the original meaning.
- Do not invent metrics, tools, responsibilities, scope, or achievements.
- Keep it to exactly one sentence.
- Keep existing technologies and acronyms if present.
- Improve clarity, strength, and relevance for the target role.
- Return only the rewritten bullet, no explanation.

Target role:
{job_title}

Important JD skills:
{", ".join(jd_skills[:8])}

Original bullet:
{original_bullet}

Deterministically refined bullet:
{refined_bullet}
""".strip()

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
    )

    text = getattr(response, "output_text", "").strip()
    return text or refined_bullet