from pathlib import Path

from parser import build_knowledge_base
from exporter import export_knowledge_base


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent

    master_path = base_dir / "inputs" / "Master Resume.docx"
    ec_path = base_dir / "inputs" / "EC Format CV.docx"
    output_path = base_dir / "outputs" / "resume_knowledge_base.json"

    kb = build_knowledge_base(master_path, ec_path)
    export_knowledge_base(kb, output_path)

    print(f"Knowledge base exported to: {output_path}")
    print(f"Projects parsed: {len(kb.projects)}")
    print(f"Certifications parsed: {len(kb.certifications)}")
    print(f"Languages parsed: {len(kb.languages)}")


if __name__ == "__main__":
    main()