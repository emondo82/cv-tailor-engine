from __future__ import annotations

from collections import Counter


SKILL_PATTERNS = {
    "SAP": ["sap", "sap cs"],
    "CRM": ["crm", "customer relationship management"],
    "Oracle": ["oracle", "oracle quotation"],
    "Salesforce": ["salesforce", "service cloud", "sales cloud", "cpq"],
    "Business Analysis": ["business analyst", "business analysis", "requirements", "requirement gathering"],
    "Stakeholder Management": ["stakeholder", "stakeholder management"],
    "Process Modelling": ["bpmn", "uml", "process modelling", "process mapping", "business process"],
    "Digital Transformation": ["digital transformation", "transformation"],
    "Integration": ["integration", "middleware", "mulesoft", "informatica", "erp"],
    "Enterprise Systems": ["enterprise systems", "enterprise", "downstream systems"],
    "Agile Delivery": ["agile", "scrum", "sprint", "backlog"],
    "Product Support": ["product", "product owner", "roadmap", "delivery"],
    "SQL": ["sql", "data analysis", "reporting", "analytics"],
    "Testing": ["uat", "sit", "testing", "test scripts", "quality assurance"],
    "Front Office": ["front-office", "front office"],
    "Quotation / Pricing": ["quotation", "pricing", "quote"],
    "JIRA": ["jira"],
    "Confluence": ["confluence"],
    "Lucidchart": ["lucidchart"],
    "Miro": ["miro"],
    "Visio": ["visio"],
}


def extract_jd_skills(job_text: str) -> list[str]:
    text = job_text.lower()
    scores = Counter()

    for skill_name, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                scores[skill_name] += 1

    return [skill for skill, _count in scores.most_common()]


if __name__ == "__main__":
    sample = """
    Schneider Electric is looking for an SAP CS, CRM and Oracle Quotation Business Analyst
    with business analysis, stakeholder management, digital transformation, and front-office experience.
    """
    print(extract_jd_skills(sample))