from __future__ import annotations


def classify_company_style(job_text: str) -> dict:
    text = job_text.lower()

    enterprise_keywords = [
        "bank", "banking", "investment bank", "capital markets", "trading",
        "financial services", "regulatory", "wealth management", "payments",
        "custodian", "treasury", "morgan stanley", "credit suisse", "citi",
        "global", "enterprise", "front-office", "front office", "digital transformation",
        "sap", "oracle", "crm", "quotation", "multi-billion", "services business",
        "schneider electric", "end-to-end", "end to end"
    ]

    fintech_keywords = [
        "fintech", "startup", "scale-up", "scaleup", "product-led", "saas",
        "fast-paced", "high-growth", "high growth", "innovation", "ownership",
        "experimentation", "seon"
    ]

    public_sector_keywords = [
        "public sector", "government", "commission", "european commission",
        "public administration", "policy", "ministry", "ngo",
        "world health organization", "who", "united nations", "eu institution",
        "european union institution"
    ]

    consulting_keywords = [
        "consulting", "client-facing", "client facing", "advisory",
        "transformation", "business transformation", "workshop", "facilitation",
        "process improvement", "stakeholder management"
    ]

    scores = {
        "enterprise": sum(1 for kw in enterprise_keywords if kw in text),
        "fintech": sum(1 for kw in fintech_keywords if kw in text),
        "public_sector": sum(1 for kw in public_sector_keywords if kw in text),
        "consulting": sum(1 for kw in consulting_keywords if kw in text),
    }

    best_style = max(scores, key=scores.get)
    best_score = scores[best_style]

    if best_score == 0:
        return {
            "style": "general",
            "reason": "No strong company-style signals detected; using general professional style.",
            "scores": scores,
        }

    reasons = {
        "enterprise": "Detected enterprise, corporate transformation, or large-company language.",
        "fintech": "Detected fintech, startup, SaaS, or high-growth language.",
        "public_sector": "Detected clear public-sector, NGO, or institutional language.",
        "consulting": "Detected consulting, facilitation, or transformation language.",
    }

    return {
        "style": best_style,
        "reason": reasons[best_style],
        "scores": scores,
    }


def style_heading(style_result: dict) -> str:
    style = style_result.get("style", "general")

    labels = {
        "enterprise": "Enterprise / Corporate Style",
        "fintech": "Fintech / Startup Style",
        "public_sector": "Public Sector / Institutional Style",
        "consulting": "Consulting / Transformation Style",
        "general": "General Professional Style",
    }

    return labels.get(style, "General Professional Style")