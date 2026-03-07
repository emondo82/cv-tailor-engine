from __future__ import annotations

import re
from typing import List, Dict


SKILL_ALIASES = {
    "CRM": ["crm", "salesforce", "service cloud", "sales cloud", "cpq"],
    "SAP": ["sap", "erp", "sap sd", "sap cs", "sap ps"],
    "Oracle": ["oracle", "oracle cpq", "oracle erp"],
    "Integration": ["integration", "middleware", "mulesoft", "informatica", "esb", "api", "soap", "rest"],
    "Testing": ["uat", "testing", "test", "test script", "acceptance criteria", "validation"],
    "Stakeholder Management": ["stakeholder", "workshop", "interview", "alignment"],
    "Quotation / Pricing": ["quotation", "pricing", "quote", "cpq", "pricefx"],
    "Business Analysis": ["business analysis", "requirements", "functional specification", "use case"],
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_search_terms(skill: str) -> List[str]:
    if skill in SKILL_ALIASES:
        return [normalize_text(term) for term in SKILL_ALIASES[skill]]

    return [normalize_text(skill)]


def build_resume_text(resume: dict) -> str:
    parts: List[str] = []

    parts.append(resume.get("summary", ""))

    for skill in resume.get("skills", []):
        parts.append(skill)

    for project in resume.get("selected_projects", []):
        parts.append(project.get("company", ""))
        parts.append(project.get("role", ""))
        parts.extend(project.get("responsibilities", []) or [])
        parts.extend(project.get("technologies", []) or [])

    for cert in resume.get("certifications", []):
        if isinstance(cert, dict):
            parts.append(cert.get("name", ""))
        else:
            parts.append(str(cert))

    return normalize_text(" ".join(parts))


def calculate_ats_coverage(jd_skills: List[str], resume: dict) -> Dict:
    resume_text = build_resume_text(resume)

    matched: List[str] = []
    missing: List[str] = []
    details: Dict[str, bool] = {}

    for skill in jd_skills:
        search_terms = get_search_terms(skill)
        is_matched = any(term and term in resume_text for term in search_terms)

        details[skill] = is_matched

        if is_matched:
            matched.append(skill)
        else:
            missing.append(skill)

    total = len(jd_skills)
    coverage_percent = round((len(matched) / total) * 100) if total else 0

    return {
        "matched": matched,
        "missing": missing,
        "coverage_percent": coverage_percent,
        "details": details,
    }