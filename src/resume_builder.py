from pathlib import Path
import json
from collections import Counter

from job_matcher import match_projects, load_job_description
from resume_exporter import export_markdown
from docx_exporter import export_resume_to_docx

def load_knowledge_base(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_top_skills(projects, max_skills=12):
    skill_counter = Counter()

    for project in projects:
        for tech in project.get("technologies", []) or []:
            cleaned = tech.strip()
            if cleaned:
                skill_counter[cleaned] += 1

    return [skill for skill, count in skill_counter.most_common(max_skills)]


def detect_job_signals(job_text: str):
    text = job_text.lower()

    signals = {
        "crm_salesforce": any(word in text for word in [
            "salesforce", "crm", "cpq", "service cloud", "sales cloud"
        ]),
        "product_delivery": any(word in text for word in [
            "product", "roadmap", "backlog", "product owner", "delivery"
        ]),
        "banking_finance": any(word in text for word in [
            "bank", "banking", "financial", "finance", "regulatory", "trading", "payments"
        ]),
        "public_sector": any(word in text for word in [
            "commission", "public sector", "ngo", "institution", "government", "european union", "who"
        ]),
        "process_modelling": any(word in text for word in [
            "bpmn", "uml", "process modelling", "process mapping", "business process"
        ]),
        "integration": any(word in text for word in [
            "integration", "sap", "mulesoft", "informatica", "enterprise systems", "erp"
        ]),
        "data_analysis": any(word in text for word in [
            "sql", "data analysis", "reporting", "analytics", "data modelling"
        ]),
        "ai_digital_transformation": any(word in text for word in [
            "ai", "digital transformation", "automation", "innovation"
        ]),
    }

    return signals


def generate_tailored_summary(kb, job_text: str) -> str:
    signals = detect_job_signals(job_text)

    intro = (
        "Senior IT Business Analyst and Product Manager with over 18 years of "
        "experience delivering business-critical transformation initiatives across "
        "international enterprise environments."
    )

    focus_parts = []

    if signals["crm_salesforce"]:
        focus_parts.append(
            "Strong experience across Salesforce ecosystems, CRM process improvement, "
            "CPQ-related change, and customer-facing service operations"
        )

    if signals["product_delivery"]:
        focus_parts.append(
            "Experienced in product backlog management, roadmap support, requirements "
            "prioritisation, and cross-functional delivery collaboration"
        )

    if signals["banking_finance"]:
        focus_parts.append(
            "Background includes work across Tier-1 financial institutions covering "
            "regulatory, data, integration, and operational change initiatives"
        )

    if signals["public_sector"]:
        focus_parts.append(
            "Also brings experience from international and public-sector environments, "
            "including the European Commission and the World Health Organization"
        )

    if signals["process_modelling"]:
        focus_parts.append(
            "Advanced capability in business process modelling, requirements engineering, "
            "and translating business needs into structured technical specifications using BPMN and UML"
        )

    if signals["integration"]:
        focus_parts.append(
            "Hands-on exposure to enterprise integration scenarios involving SAP, middleware, "
            "and downstream system alignment"
        )

    if signals["data_analysis"]:
        focus_parts.append(
            "Combines business analysis with strong analytical thinking, including SQL-driven "
            "analysis, reporting support, and data-focused problem solving"
        )

    if signals["ai_digital_transformation"]:
        focus_parts.append(
            "Brings a modern transformation mindset, including practical use of AI-supported "
            "analysis and process improvement approaches"
        )

    closing = (
        "Well positioned to bridge business and technology stakeholders, structure complex "
        "requirements, and support delivery with a strong focus on clarity, relevance, "
        "and measurable business value."
    )

    if not focus_parts:
        return kb.get("raw_master_resume_summary", intro + " " + closing)

    return intro + " " + ". ".join(focus_parts) + ". " + closing

def month_year_to_sort_value(date_str: str | None) -> int:
    if not date_str:
        return 0

    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }

    parts = date_str.strip().split()
    if len(parts) != 2:
        return 0

    month = months.get(parts[0], 0)
    try:
        year = int(parts[1])
    except ValueError:
        return 0

    return year * 100 + month


def sort_projects_reverse_chronological(projects: list[dict]) -> list[dict]:
    return sorted(
        projects,
        key=lambda p: month_year_to_sort_value(p.get("end_date") or p.get("start_date")),
        reverse=True,
    )

def build_resume(kb, job_text, top_n=6):
    ranked = match_projects(kb, job_text)
    top_projects = [p for score, p in ranked[:top_n]]
    top_projects = sort_projects_reverse_chronological(top_projects)

    resume = {
        "summary": generate_tailored_summary(kb, job_text),
        "skills": extract_top_skills(top_projects),
        "selected_projects": top_projects,
        "education": kb.get("education", []),
        "certifications": kb.get("certifications", []),
        "languages": kb.get("languages", []),
    }

    return resume


def print_summary(summary):
    print("PROFESSIONAL SUMMARY\n")
    print(summary)
    print("\n")


def print_skills(skills):
    print("CORE SKILLS\n")
    if skills:
        print(" | ".join(skills))
    else:
        print("No skills identified.")
    print("\n")


def print_experience(projects):
    print("SELECTED EXPERIENCE\n")

    for project in projects:
        company = project.get("company") or "Unknown"
        role = project.get("role") or ""
        client = project.get("client") or ""

        header = company if not role else f"{company} — {role}"
        print(header)

        if client:
            print(f"Client: {client}")

        responsibilities = project.get("responsibilities", []) or []

        for r in responsibilities[:4]:
            print(f"  • {r}")

        print()


def print_education(education):
    print("EDUCATION\n")

    if not education:
        print("No education data available.\n")
        return

    for item in education:
        degree = item.get("degree", "")
        field = item.get("field", "")
        institution = item.get("institution", "")
        start_date = item.get("start_date", "")
        end_date = item.get("end_date", "")

        line = f"{degree}"
        if field:
            line += f" in {field}"
        if institution:
            line += f" — {institution}"
        if start_date or end_date:
            line += f" ({start_date} - {end_date})"

        print(line)

    print()


def print_certifications(certifications):
    print("CERTIFICATIONS\n")

    if not certifications:
        print("No certifications available.\n")
        return

    for cert in certifications:
        name = cert.get("name", "")
        provider = cert.get("provider", "")
        date = cert.get("date", "")

        line = name
        if provider:
            line += f" — {provider}"
        if date:
            line += f" ({date})"

        print(f"• {line}")

    print()


def print_languages(languages):
    print("LANGUAGES\n")

    if not languages:
        print("No language data available.\n")
        return

    for lang in languages:
        language = lang.get("language", "")

        if lang.get("level"):
            print(f"• {language}: {lang['level']}")
        else:
            spoken = lang.get("spoken", "")
            written = lang.get("written", "")
            print(f"• {language}: Spoken {spoken}, Written {written}")

    print()


def print_resume(resume):
    print("\nTAILORED RESUME\n")

    print_summary(resume["summary"])
    print_skills(resume["skills"])
    print_experience(resume["selected_projects"])
    print_education(resume["education"])
    print_certifications(resume["certifications"])
    print_languages(resume["languages"])


def main():
    base = Path(__file__).resolve().parent.parent

    kb_path = base / "outputs" / "resume_knowledge_base.json"
    jd_path = base / "inputs" / "job_description.txt"

    kb = load_knowledge_base(kb_path)
    job_text = load_job_description(jd_path)

    resume = build_resume(kb, job_text)
    print_resume(resume)

    md_output_path = base / "outputs" / "tailored_resume.md"
    export_markdown(resume, md_output_path)
    print(f"Markdown resume exported to: {md_output_path}")

    docx_output_path = base / "outputs" / "tailored_resume.docx"
    candidate_profile = kb.get("candidate_profile", {})
    candidate_name = candidate_profile.get("name", "Tamas Kosina")
    export_resume_to_docx(
        resume,
        docx_output_path,
        candidate_name=candidate_name,
        candidate_profile=candidate_profile,
    )
    print(f"DOCX resume exported to: {docx_output_path}")


if __name__ == "__main__":
    main()