from __future__ import annotations

import json
import os
from google import genai
from dotenv import load_dotenv
load_dotenv()


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def review_bullet_with_gemini(
    original_bullet: str,
    rewritten_bullet: str,
    job_title: str,
) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
Review this rewritten CV bullet.

Return strict JSON with:
{{
  "decision": "SAFE" or "UNSAFE",
  "reason": "short reason"
}}

Rules:
- SAFE only if the rewritten bullet preserves the original meaning.
- Mark UNSAFE if it adds unsupported claims, tools, metrics, ownership, or achievements.
- Ignore minor wording changes if the meaning stays intact.
- No markdown, no commentary, JSON only.

Job title:
{job_title}

Original bullet:
{original_bullet}

Rewritten bullet:
{rewritten_bullet}
""".strip()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    raw = (response.text or "").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"decision": "UNSAFE", "reason": "Validator returned invalid JSON"}

    decision = str(data.get("decision", "")).strip().upper()
    reason = str(data.get("reason", "")).strip()

    if decision not in {"SAFE", "UNSAFE"}:
        return {"decision": "UNSAFE", "reason": "Validator returned invalid decision"}

    return {"decision": decision, "reason": reason}