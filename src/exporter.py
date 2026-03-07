from __future__ import annotations

import json
from pathlib import Path

from models import ResumeKnowledgeBase


def export_knowledge_base(kb: ResumeKnowledgeBase, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(kb.model_dump(), f, indent=2, ensure_ascii=False)