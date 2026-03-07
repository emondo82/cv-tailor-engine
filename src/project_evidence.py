from typing import List, Dict


def extract_project_evidence(projects: List[dict], jd_skills: List[str]) -> List[Dict]:
    results = []

    for project in projects:
        combined_text = " ".join(project.get("responsibilities", []))
        combined_text += " " + " ".join(project.get("technologies", []) or [])
        combined_text = combined_text.lower()

        matched = []

        for skill in jd_skills:
            if skill.lower() in combined_text:
                matched.append(skill)

        results.append({
            "company": project.get("company", ""),
            "role": project.get("role", ""),
            "matched_skills": matched,
        })

    return results