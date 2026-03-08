from __future__ import annotations

import os
import re

from bullet_refiner import refine_bullet
from llm_bullet_writer import rewrite_bullet_with_openai
from llm_bullet_validator import review_bullet_with_gemini
from dotenv import load_dotenv
load_dotenv()


USE_LLM_BULLET_REFINER = os.getenv("USE_LLM_BULLET_REFINER", "false").lower() == "true"


def preserves_acronyms(original: str, rewritten: str) -> bool:
    original_acronyms = set(re.findall(r"\b[A-Z]{2,}\b", original))
    rewritten_acronyms = set(re.findall(r"\b[A-Z]{2,}\b", rewritten))
    return original_acronyms.issubset(rewritten_acronyms)


def safe_llm_refine_bullet(
    bullet: str,
    job_title: str,
    jd_skills: list[str],
) -> tuple[str, dict]:
    deterministic = refine_bullet(bullet)

    if not USE_LLM_BULLET_REFINER:
        return deterministic, {
            "mode": "deterministic_only",
            "accepted": False,
            "reason": "LLM refiner disabled",
        }

    rewritten = rewrite_bullet_with_openai(
        original_bullet=bullet,
        refined_bullet=deterministic,
        job_title=job_title,
        jd_skills=jd_skills,
    )

    if not rewritten.strip():
        return deterministic, {
            "mode": "fallback",
            "accepted": False,
            "reason": "Empty OpenAI rewrite",
        }

    if not preserves_acronyms(bullet, rewritten):
        return deterministic, {
            "mode": "fallback",
            "accepted": False,
            "reason": "Acronym preservation check failed",
        }

    review = review_bullet_with_gemini(
        original_bullet=bullet,
        rewritten_bullet=rewritten,
        job_title=job_title,
    )

    if review["decision"] == "SAFE":
        return rewritten.strip(), {
            "mode": "llm_accepted",
            "accepted": True,
            "reason": review["reason"],
        }

    return deterministic, {
        "mode": "fallback",
        "accepted": False,
        "reason": review["reason"],
    }