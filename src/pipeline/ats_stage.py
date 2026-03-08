from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any

from ats_coverage import build_resume_text, get_search_terms, normalize_text


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize_for_match(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(normalize_text(text))


def _contains_term_tokens(text_tokens: list[str], term: str) -> bool:
    term_tokens = _tokenize_for_match(term)
    if not term_tokens or not text_tokens:
        return False

    if len(term_tokens) == 1:
        return term_tokens[0] in set(text_tokens)

    window = len(term_tokens)
    limit = len(text_tokens) - window + 1
    if limit < 1:
        return False

    for i in range(limit):
        if text_tokens[i:i + window] == term_tokens:
            return True

    return False


def _collect_project_bullets(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_rows: list[dict[str, Any]] = []

    for project in projects:
        company = str(project.get("company") or "")
        role = str(project.get("role") or "")
        responsibilities = project.get("responsibilities", []) or []

        for bullet in responsibilities:
            bullet_text = str(bullet or "").strip()
            if not bullet_text:
                continue

            evidence_rows.append(
                {
                    "company": company,
                    "role": role,
                    "bullet": bullet_text,
                    "tokens": _tokenize_for_match(bullet_text),
                }
            )

    return evidence_rows


def _find_evidence_for_skill(
    skill: str,
    bullet_rows: list[dict[str, Any]],
    search_terms: list[str],
) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    matches: list[dict[str, str]] = []

    for row in bullet_rows:
        bullet_tokens = row["tokens"]
        if not any(_contains_term_tokens(bullet_tokens, term) for term in search_terms):
            continue

        key = (row["company"], row["role"], row["bullet"])
        if key in seen:
            continue

        seen.add(key)
        matches.append(
            {
                "company": row["company"],
                "role": row["role"],
                "bullet": row["bullet"],
                "skill": skill,
            }
        )

    return matches


def _resume_match_for_skill(resume_tokens: list[str], search_terms: list[str]) -> bool:
    return any(_contains_term_tokens(resume_tokens, term) for term in search_terms)


def analyse_ats_coverage(
    jd_skills: list[str],
    source_projects: list[dict[str, Any]],
    resume: dict[str, Any],
) -> dict[str, Any]:
    source_rows = _collect_project_bullets(source_projects)
    rewritten_rows = _collect_project_bullets(resume.get("selected_projects", []) or [])
    resume_text = build_resume_text(resume)
    resume_tokens = _tokenize_for_match(resume_text)

    matched_keywords: list[str] = []
    uncovered_keywords: list[str] = []
    details: dict[str, bool] = {}
    evidence_mapping: dict[str, dict[str, Any]] = {}

    for skill in jd_skills:
        search_terms = [normalize_text(term) for term in get_search_terms(skill)]

        source_matches = _find_evidence_for_skill(skill, source_rows, search_terms)
        rewritten_matches = _find_evidence_for_skill(skill, rewritten_rows, search_terms)
        final_resume_match = _resume_match_for_skill(resume_tokens, search_terms)

        is_matched = bool(source_matches or rewritten_matches or final_resume_match)
        details[skill] = is_matched

        if is_matched:
            matched_keywords.append(skill)
        else:
            uncovered_keywords.append(skill)

        evidence_mapping[skill] = {
            "search_terms": search_terms,
            "source_bullets": source_matches,
            "rewritten_bullets": rewritten_matches,
            "final_resume_match": final_resume_match,
        }

    total = len(jd_skills)
    coverage_percent = round((len(matched_keywords) / total) * 100) if total else 0

    return {
        "matched": matched_keywords,
        "missing": uncovered_keywords,
        "coverage_percent": coverage_percent,
        "details": details,
        "matched_keywords": matched_keywords,
        "uncovered_keywords": uncovered_keywords,
        "evidence_mapping": evidence_mapping,
    }


def _safe_job_name(job_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "_", job_name.strip())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "application"


def _write_ats_report_json(report: dict[str, Any], output_path: Path) -> None:
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_ats_report_md(report: dict[str, Any], output_path: Path) -> None:
    matched = report.get("matched_keywords", []) or []
    uncovered = report.get("uncovered_keywords", []) or []
    evidence_mapping = report.get("evidence_mapping", {}) or {}

    lines: list[str] = []
    lines.append("# ATS Coverage Report")
    lines.append("")
    lines.append(f"- Coverage: {report.get('coverage_percent', 0)}%")
    lines.append(f"- Matched keywords: {len(matched)}")
    lines.append(f"- Uncovered keywords: {len(uncovered)}")
    lines.append("")

    lines.append("## Matched Keywords")
    lines.append("")
    if matched:
        for keyword in matched:
            lines.append(f"- {keyword}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Uncovered Keywords")
    lines.append("")
    if uncovered:
        for keyword in uncovered:
            lines.append(f"- {keyword}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Evidence Mapping")
    lines.append("")
    for skill, evidence in evidence_mapping.items():
        lines.append(f"### {skill}")
        lines.append("")
        search_terms = evidence.get("search_terms", []) or []
        lines.append(f"- Search terms: {', '.join(search_terms) if search_terms else 'None'}")
        lines.append(f"- Final resume match: {evidence.get('final_resume_match', False)}")
        lines.append("")

        source_bullets = evidence.get("source_bullets", []) or []
        lines.append("- Source bullets:")
        if source_bullets:
            for row in source_bullets:
                company = row.get("company", "")
                role = row.get("role", "")
                bullet = row.get("bullet", "")
                header = f"{company} ({role})" if role else company
                lines.append(f"  - {header}: {bullet}")
        else:
            lines.append("  - None")
        lines.append("")

        rewritten_bullets = evidence.get("rewritten_bullets", []) or []
        lines.append("- Rewritten bullets:")
        if rewritten_bullets:
            for row in rewritten_bullets:
                company = row.get("company", "")
                role = row.get("role", "")
                bullet = row.get("bullet", "")
                header = f"{company} ({role})" if role else company
                lines.append(f"  - {header}: {bullet}")
        else:
            lines.append("  - None")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_ats_stage(
    *,
    outputs_dir: Path,
    job_name: str,
    jd_skills: list[str],
    source_projects: list[dict[str, Any]],
    resume: dict[str, Any],
) -> dict[str, Any]:
    outputs_dir.mkdir(parents=True, exist_ok=True)

    report = analyse_ats_coverage(
        jd_skills=jd_skills,
        source_projects=source_projects,
        resume=resume,
    )

    safe_name = _safe_job_name(job_name)
    md_path = outputs_dir / f"{safe_name}_ats_report.md"
    json_path = outputs_dir / f"{safe_name}_ats_report.json"

    _write_ats_report_md(report, md_path)
    _write_ats_report_json(report, json_path)

    return {
        "ats_coverage": report,
        "report_md_path": md_path,
        "report_json_path": json_path,
    }
