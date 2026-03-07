from pathlib import Path
import json
import re

from job_matcher import match_projects, load_job_description
from cover_letter_exporter import export_cover_letter_to_docx
from style_classifier import classify_company_style


def load_knowledge_base(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_cover_letter_signals(job_text: str):
    text = job_text.lower()

    return {
        "crm_salesforce": any(word in text for word in [
            "salesforce", "crm", "cpq", "service cloud", "sales cloud"
        ]),
        "product_delivery": any(word in text for word in [
            "product", "roadmap", "backlog", "delivery", "product owner"
        ]),
        "banking_finance": any(word in text for word in [
            "bank", "banking", "financial", "finance", "regulatory", "payments", "trading"
        ]),
        "public_sector": any(word in text for word in [
            "commission", "public sector", "institution", "government", "ngo", "european union"
        ]),
        "process_modelling": any(word in text for word in [
            "bpmn", "uml", "process modelling", "process mapping", "business process"
        ]),
        "integration": any(word in text for word in [
            "integration", "sap", "mulesoft", "informatica", "erp", "middleware"
        ]),
    }

def extract_job_title(job_text: str) -> str | None:
    lines = [line.strip() for line in job_text.splitlines() if line.strip()]

    patterns = [
        r"(?i)^job title[:\-]\s*(.+)$",
        r"(?i)^position[:\-]\s*(.+)$",
        r"(?i)^role[:\-]\s*(.+)$",
        r"(?i)^title[:\-]\s*(.+)$",
    ]

    for line in lines[:20]:
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                title = cleanup_extracted_text(match.group(1))
                if title.lower() not in {"the job", "about the job"}:
                    return title

    # LinkedIn fallback: usually a standalone title line near the top
    for line in lines[:12]:
        cleaned = cleanup_extracted_text(line)
        lowered = cleaned.lower()

        if lowered in {
            "about the job", "apply", "save", "hybrid", "full-time",
            "promoted by hirer", "responses managed off linkedin"
        }:
            continue

        if 2 <= len(cleaned.split()) <= 8:
            if any(word in lowered for word in ["analyst", "manager", "owner", "lead", "consultant", "architect"]):
                return cleaned

    return None

def extract_company_name(job_text: str) -> str | None:
    lines = [line.strip() for line in job_text.splitlines() if line.strip()]

    # 1. Strong LinkedIn-style pattern: "Company logo for, Morgan Stanley."
    logo_match = re.search(r"(?im)^Company logo for,\s*(.+?)\.?\s*$", job_text)
    if logo_match:
        company = cleanup_extracted_text(logo_match.group(1))
        if company and company.lower() not in {"the job", "job"}:
            return company

    # 2. Explicit company labels only
    explicit_patterns = [
        r"(?i)^company[:\-]\s*(.+)$",
        r"(?i)^company name[:\-]\s*(.+)$",
        r"(?i)^employer[:\-]\s*(.+)$",
    ]

    for line in lines[:25]:
        for pattern in explicit_patterns:
            match = re.match(pattern, line)
            if match:
                company = cleanup_extracted_text(match.group(1))
                if company and company.lower() not in {"the job", "job"}:
                    return company

    # 3. Fallback: repeated proper-name line near the top
    # LinkedIn dumps often have the company name as a standalone line
    for line in lines[:12]:
        cleaned = cleanup_extracted_text(line)
        lowered = cleaned.lower()

        if lowered in {
            "about the job", "apply", "save", "hybrid", "full-time",
            "promoted by hirer", "responses managed off linkedin"
        }:
            continue

        if 1 <= len(cleaned.split()) <= 4 and any(c.isupper() for c in cleaned):
            if cleaned not in {"Technical Business Analyst"}:
                return cleaned

    return None

def smart_title_case(text: str) -> str:
    if not text:
        return text

    small_words = {"and", "or", "of", "the", "at", "in", "to", "for"}
    words = text.split()
    result = []

    for i, word in enumerate(words):
        if word.isupper():
            result.append(word)
            continue

        lower_word = word.lower()

        if i > 0 and lower_word in small_words:
            result.append(lower_word)
        else:
            result.append(lower_word.capitalize())

    return " ".join(result)

def cleanup_extracted_text(text: str) -> str:
    cleaned = " ".join(text.split()).strip(" -,:")
    return cleaned


def generate_opening(job_text: str, job_title: str | None, company_name: str | None) -> str:
    company_display = smart_title_case(company_name) if company_name else None
    title_display = smart_title_case(job_title) if job_title else None

    greeting = f"Dear {company_display} Recruitment Team," if company_display else "Dear Hiring Team,"

    if title_display and company_display:
        opening_line = (
            f"I am writing to express my interest in the {title_display} position at {company_display}. "
        )
    elif title_display:
        opening_line = (
            f"I am writing to express my interest in the {title_display} position. "
        )
    else:
        opening_line = (
            "I am writing to express my interest in this opportunity. "
        )

    body = (
        "With over 18 years of experience in business analysis, product support, "
        "digital transformation, and cross-functional delivery, I bring a strong track record "
        "of translating business needs into structured, actionable solutions across enterprise and international environments."
    )

    return f"{greeting}\n\n{opening_line}{body}"


def generate_fit_paragraph(job_text: str) -> str:
    signals = detect_cover_letter_signals(job_text)
    style_result = classify_company_style(job_text)
    style = style_result.get("style", "general")

    parts = []

    if signals["crm_salesforce"]:
        parts.append(
            "My background includes substantial experience across Salesforce-related environments, CRM process improvement, and customer-facing operational change"
        )

    if signals["product_delivery"]:
        parts.append(
            "I have also worked closely with product backlogs, roadmap support, prioritisation, and delivery coordination"
        )

    if signals["banking_finance"]:
        parts.append(
            "In addition, I bring experience from Tier-1 financial institutions, where I supported regulatory, data, and operational change initiatives"
        )

    if signals["public_sector"]:
        parts.append(
            "My experience also includes work in international and institutional environments such as the European Commission and the World Health Organization"
        )

    if signals["process_modelling"]:
        parts.append(
            "A core strength of mine is process modelling and requirements engineering using BPMN and UML"
        )

    if signals["integration"]:
        parts.append(
            "I also have hands-on exposure to enterprise integration scenarios involving SAP, middleware, and downstream systems"
        )

    if not parts:
        if style == "enterprise":
            return (
                "My experience spans business analysis, stakeholder coordination, structured requirements work, "
                "and support for complex change initiatives in enterprise environments."
            )
        if style == "fintech":
            return (
                "My experience spans business analysis, product support, and practical transformation work in fast-moving digital environments."
            )
        if style == "public_sector":
            return (
                "My experience spans business analysis, stakeholder coordination, and structured transformation support in institutional environments."
            )
        if style == "consulting":
            return (
                "My experience spans business analysis, facilitation, process improvement, and support for complex transformation initiatives."
            )
        return (
            "My experience spans business analysis, requirements engineering, stakeholder collaboration, "
            "and support for technology-enabled business transformation."
        )

    return ". ".join(parts) + "."


def project_evidence_line(project: dict) -> str:
    company = smart_title_case(project.get("company") or "Unknown company")
    client = smart_title_case(project.get("client") or "")
    responsibilities = project.get("responsibilities", []) or []

    if responsibilities:
        evidence = responsibilities[0].strip()
    else:
        evidence = (project.get("project_description") or "supported business analysis and delivery activities").strip()

    if evidence:
        evidence = evidence[:1].lower() + evidence[1:]

    if client:
        return f"While supporting {company} for {client}, I {evidence}."
    return f"At {company}, I {evidence}."


def generate_evidence_paragraph(top_projects: list[dict]) -> str:
    lines = [project_evidence_line(p) for p in top_projects[:3]]

    return (
    "Relevant examples from my background include the following. "
    + " ".join(lines)
    + " These experiences strengthened my ability to work across stakeholders, "
      "clarify requirements, and support practical solution delivery."
    )


def generate_closing() -> str:
    return (
        "I would welcome the opportunity to discuss how my background could support your team and objectives. "
        "Thank you for your consideration.\n\n"
        "Kind regards,\n"
        "Tamas Kosina"
    )


def build_cover_letter(kb: dict, job_text: str, top_n: int = 3) -> str:
    ranked = match_projects(kb, job_text)
    top_projects = [p for score, p in ranked[:top_n]]

    job_title = extract_job_title(job_text)
    company_name = extract_company_name(job_text)
    style_result = classify_company_style(job_text)

    sections = [
        generate_opening(job_text, job_title, company_name),
        generate_fit_paragraph(job_text),
        generate_evidence_paragraph(top_projects),
        generate_closing(),
    ]

    return "\n\n".join(sections)


def main():
    base = Path(__file__).resolve().parent.parent

    kb_path = base / "outputs" / "resume_knowledge_base.json"
    jd_path = base / "inputs" / "job_description.txt"

    md_output_path = base / "outputs" / "tailored_cover_letter.md"
    docx_output_path = base / "outputs" / "tailored_cover_letter.docx"

    kb = load_knowledge_base(kb_path)
    job_text = load_job_description(jd_path)

    cover_letter = build_cover_letter(kb, job_text)

    print("\nTAILORED COVER LETTER\n")
    print(cover_letter)
    print()

    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(cover_letter)

    print(f"Cover letter exported to: {md_output_path}")

    candidate_profile = kb.get("candidate_profile", {})
    candidate_name = candidate_profile.get("name", "Tamas Kosina")

    export_cover_letter_to_docx(
        cover_letter,
        docx_output_path,
        candidate_name=candidate_name,
        candidate_profile=candidate_profile,
    )

    print(f"DOCX cover letter exported to: {docx_output_path}")


if __name__ == "__main__":
    main()