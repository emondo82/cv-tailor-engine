from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def write_run_metadata(
    output_dir: Path,
    company_name: str,
    job_title: str,
    output_slug: str,
    jd_skills: list[str],
    project_matches: list[dict],
    files: dict,
) -> None:
    metadata = {
        "company": company_name,
        "job_title": job_title,
        "output_slug": output_slug,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "jd_skills": jd_skills,
        "project_matches": project_matches,
        "files": files,
    }

    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Created: {metadata_path}")