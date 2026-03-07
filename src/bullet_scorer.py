from __future__ import annotations

import re
from typing import List


DOMAIN_KEYWORDS = {
    "banking": ["bank", "banking", "loan", "lending", "finance", "financial", "payments"],
    "salesforce": ["salesforce", "service cloud", "sales cloud", "cpq"],
    "sap": ["sap", "erp", "sap sd", "sap cs", "sap ps"],
    "integration": ["integration", "middleware", "mulesoft", "informatica", "esb", "api", "soap", "rest"],
    "process": ["process", "bpmn", "uml", "workshop", "mapping", "as-is", "to-be"],
    "testing": ["uat", "testing", "test", "test script", "acceptance criteria", "validation"],
    "quotation": ["quotation", "pricing", "quote", "cpq", "pricefx", "oracle cpq"],
}


IMPORTANT_ACTIONS = [
    "analysed",
    "analyzed",
    "defined",
    "translated",
    "gathered",
    "elicited",
    "validated",
    "verified",
    "mapped",
    "conducted",
    "created",
    "managed",
    "supported",
    "coordinated",
]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokenize(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-z0-9\s\-/]", " ", text.lower())
    return [token for token in cleaned.split() if len(token) > 1]


def score_bullet(
    bullet: str,
    jd_skills: List[str],
    job_text: str,
    project_technologies: List[str] | None = None,
) -> int:
    bullet_norm = normalize_text(bullet)
    bullet_tokens = set(tokenize(bullet))
    job_norm = normalize_text(job_text)
    tech_norm = [normalize_text(t) for t in (project_technologies or [])]

    score = 0

    # 1. Direct JD skill hits
    for skill in jd_skills:
        skill_norm = normalize_text(skill)
        if skill_norm and skill_norm in bullet_norm:
            score += 5
        else:
            skill_tokens = set(tokenize(skill))
            if skill_tokens and skill_tokens.intersection(bullet_tokens):
                score += 3

    # 2. Technology reinforcement
    for tech in tech_norm:
        if tech and tech in bullet_norm:
            score += 2

    # 3. Domain keyword matching based on JD
    for keywords in DOMAIN_KEYWORDS.values():
        jd_has_domain = any(keyword in job_norm for keyword in keywords)
        if jd_has_domain and any(keyword in bullet_norm for keyword in keywords):
            score += 2

    # 4. Strong action verbs
    if any(action in bullet_norm for action in IMPORTANT_ACTIONS):
        score += 1

    # 5. Bonus for exact high-value terms
    exact_terms = [
        "uat",
        "bpmn",
        "uml",
        "jira",
        "confluence",
        "oracle",
        "sap",
        "crm",
        "salesforce",
        "integration",
        "api",
        "pricing",
        "quotation",
        "cpq",
    ]
    for term in exact_terms:
        if term in bullet_norm and term in job_norm:
            score += 2

    return score