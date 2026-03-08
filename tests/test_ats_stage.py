from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline.ats_stage import analyse_ats_coverage  # noqa: E402


def test_analyse_ats_coverage_maps_evidence_and_uncovered_keywords() -> None:
    jd_skills = ["SAP", "CRM", "Testing"]

    source_projects = [
        {
            "company": "Example Corp",
            "role": "Business Analyst",
            "responsibilities": [
                "Led SAP integration workshops with stakeholders.",
                "Defined enterprise process documentation.",
            ],
        }
    ]

    resume = {
        "summary": "Business analyst focused on enterprise CRM transformation.",
        "skills": ["SAP", "CRM"],
        "selected_projects": [
            {
                "company": "Example Corp",
                "role": "Business Analyst",
                "responsibilities": [
                    "Supported CRM process redesign and stakeholder alignment.",
                ],
                "technologies": ["SAP", "CRM"],
            }
        ],
        "certifications": [],
    }

    report = analyse_ats_coverage(
        jd_skills=jd_skills,
        source_projects=source_projects,
        resume=resume,
    )

    assert report["matched_keywords"] == ["SAP", "CRM"]
    assert report["uncovered_keywords"] == ["Testing"]
    assert report["coverage_percent"] == 67

    sap_source = report["evidence_mapping"]["SAP"]["source_bullets"]
    assert len(sap_source) == 1
    assert "sap integration workshops" in sap_source[0]["bullet"].lower()

    crm_rewritten = report["evidence_mapping"]["CRM"]["rewritten_bullets"]
    assert len(crm_rewritten) == 1
    assert "crm process redesign" in crm_rewritten[0]["bullet"].lower()

    assert report["evidence_mapping"]["Testing"]["final_resume_match"] is False


def test_analyse_ats_coverage_does_not_match_erp_inside_enterprise() -> None:
    jd_skills = ["SAP"]

    source_projects = [
        {
            "company": "Example Corp",
            "role": "Business Analyst",
            "responsibilities": [
                "Defined enterprise process documentation.",
            ],
        }
    ]

    resume = {
        "summary": "Business analyst focused on process clarity.",
        "skills": [],
        "selected_projects": [
            {
                "company": "Example Corp",
                "role": "Business Analyst",
                "responsibilities": [
                    "Defined enterprise process documentation.",
                ],
                "technologies": [],
            }
        ],
        "certifications": [],
    }

    report = analyse_ats_coverage(
        jd_skills=jd_skills,
        source_projects=source_projects,
        resume=resume,
    )

    assert report["matched_keywords"] == []
    assert report["uncovered_keywords"] == ["SAP"]
    assert report["coverage_percent"] == 0
    assert report["evidence_mapping"]["SAP"]["source_bullets"] == []
    assert report["evidence_mapping"]["SAP"]["rewritten_bullets"] == []
    assert report["evidence_mapping"]["SAP"]["final_resume_match"] is False
