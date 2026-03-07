from pathlib import Path
import json
import re


def load_knowledge_base(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_job_description(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().lower()


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-\+]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    stop_words = {
        "the", "and", "for", "with", "a", "an", "to", "of", "in", "on", "by",
        "is", "are", "we", "looking", "experience", "using", "within", "across",
        "senior", "role"
    }
    words = normalize_text(text).split()
    return [w for w in words if len(w) > 2 and w not in stop_words]


def build_project_searchable_text(project: dict) -> str:
    parts = [
        project.get("company") or "",
        project.get("project_name") or "",
        project.get("role") or "",
        project.get("client") or "",
        project.get("project_description") or "",
        " ".join(project.get("responsibilities", []) or []),
        " ".join(project.get("technologies", []) or []),
        project.get("domain") or "",
    ]
    return normalize_text(" ".join(parts))


def score_project(project: dict, job_text: str) -> int:
    searchable = build_project_searchable_text(project)
    job_tokens = tokenize(job_text)

    score = 0
    for token in job_tokens:
        if token in searchable:
            score += 1

    # Bonus scoring for more important signals
    bonuses = [
        "salesforce", "crm", "cpq", "bpmn", "uml", "integration",
        "stakeholder", "jira", "confluence", "sap", "mulesoft"
    ]
    for bonus in bonuses:
        if bonus in job_tokens and bonus in searchable:
            score += 2

    return score


def match_projects(kb: dict, job_text: str):
    scored = []

    for project in kb["projects"]:
        score = score_project(project, job_text)
        scored.append((score, project))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored


def short_description(text: str, max_len: int = 55) -> str:
    if not text:
        return ""
    text = " ".join(text.split())
    return text if len(text) <= max_len else text[:max_len].rstrip() + "..."


def project_label(project: dict) -> str:
    company = (project.get("company") or "Unknown company").strip()
    project_name = (project.get("project_name") or "").strip()
    client = (project.get("client") or "").strip()
    description = (project.get("project_description") or "").strip()

    if project_name:
        return f"{company} — {project_name}"
    if client:
        return f"{company} — Client: {client}"
    if description:
        return f"{company} — {short_description(description)}"
    return company

def main():
    base = Path(__file__).resolve().parent.parent

    kb_path = base / "outputs" / "resume_knowledge_base.json"
    jd_path = base / "inputs" / "job_description.txt"

    kb = load_knowledge_base(kb_path)
    jd = load_job_description(jd_path)

    results = match_projects(kb, jd)

    print("\nTop matching projects:\n")

    for score, project in results[:8]:
        print(f"{score:>2} — {project_label(project)}")


if __name__ == "__main__":
    main()