from __future__ import annotations

from job_matcher import match_projects
from project_evidence import extract_project_evidence


def run_match_stage(kb: dict, job_text: str, jd_skills: list[str], top_n: int = 6) -> dict:
    ranked = match_projects(kb, job_text)
    top_projects = [project for score, project in ranked[:top_n]]
    project_matches = extract_project_evidence(top_projects, jd_skills)

    return {
        "top_projects": top_projects,
        "project_matches": project_matches,
    }