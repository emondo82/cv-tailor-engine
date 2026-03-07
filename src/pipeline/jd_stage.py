from __future__ import annotations

from pathlib import Path
import re

from jd_skill_extractor import extract_jd_skills


def load_job_text(job_description_path: Path) -> str:
    if not job_description_path.exists():
        raise FileNotFoundError(f"Missing job description: {job_description_path}")
    return job_description_path.read_text(encoding="utf-8").strip()


def infer_company_name(job_text: str) -> str:
    lines = [line.strip() for line in job_text.splitlines() if line.strip()]

    ignore_patterns = [
        "share",
        "show more options",
        "hybrid",
        "full-time",
        "full time",
        "easy apply",
        "apply",
        "save",
        "about the job",
        "job poster",
        "reposted",
        "promoted by hirer",
        "actively reviewing applicants",
        "matches your job preferences",
        "access exclusive applicant insights",
        "retry premium",
        "meet the hiring team",
        "message",
    ]

    location_markers = [
        "budapest",
        "metropolitan area",
        "hungary",
    ]

    title_keywords = [
        "analyst",
        "manager",
        "owner",
        "consultant",
        "lead",
        "specialist",
        "architect",
        "coordinator",
        "director",
    ]

    # First strong rule: company usually appears in the first 10 lines
    # and is NOT the title, NOT a location line, NOT a UI line.
    for line in lines[:12]:
        lower = line.lower()

        if len(line) < 2 or len(line) > 100:
            continue

        if any(pattern in lower for pattern in ignore_patterns):
            continue

        if any(marker in lower for marker in location_markers):
            continue

        if any(keyword in lower for keyword in title_keywords):
            continue

        return line

    return "Target Company"

def infer_job_title(job_text: str) -> str:
    lines = [line.strip() for line in job_text.splitlines() if line.strip()]

    ignore_patterns = [
        "share",
        "show more options",
        "hybrid",
        "full-time",
        "full time",
        "easy apply",
        "apply",
        "save",
        "about the job",
        "job poster",
        "reposted",
        "promoted by hirer",
        "actively reviewing applicants",
        "matches your job preferences",
        "access exclusive applicant insights",
        "retry premium",
        "meet the hiring team",
        "message",
    ]

    location_markers = [
        "budapest",
        "metropolitan area",
        "hungary",
    ]

    title_keywords = [
        "analyst",
        "manager",
        "owner",
        "consultant",
        "lead",
        "specialist",
        "architect",
        "coordinator",
        "director",
    ]

    for line in lines[:20]:
        lower = line.lower()

        if len(line) < 8 or len(line) > 140:
            continue

        if any(pattern in lower for pattern in ignore_patterns):
            continue

        if any(marker in lower for marker in location_markers):
            continue

        if any(keyword in lower for keyword in title_keywords):
            return line

    return "Target Role"


def safe_slug(text: str, max_len: int = 120) -> str:
    text = text.replace("&", "and")
    text = re.sub(r"[\/:]+", "_", text)
    text = re.sub(r"[^A-Za-z0-9 _-]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"_+", "_", text)
    return text[:max_len].strip("_") if text else "application"


def analyse_job_description(job_text: str) -> dict:
    company_name = infer_company_name(job_text)
    job_title = infer_job_title(job_text)
    jd_skills = extract_jd_skills(job_text)
    application_slug = safe_slug(f"{company_name}_{job_title}")

    return {
        "company_name": company_name,
        "job_title": job_title,
        "jd_skills": jd_skills,
        "application_slug": application_slug,
    }