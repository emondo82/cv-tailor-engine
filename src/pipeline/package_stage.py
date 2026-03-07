from __future__ import annotations

from pathlib import Path
import shutil

from pipeline.jd_stage import safe_slug


def copy_if_exists(source: Path, target: Path) -> None:
    if source.exists():
        shutil.copy2(source, target)
        print(f"Created: {target}")


def build_file_label(job_title: str, candidate_name: str, max_len: int = 100) -> str:
    return safe_slug(f"{job_title}_{candidate_name}", max_len=max_len)

def delete_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()
        print(f"Deleted temporary file: {path}")

def package_outputs(
    outputs_dir: Path,
    application_dir: Path,
    file_label: str,
) -> dict:
    generic_resume_docx = outputs_dir / "tailored_resume.docx"
    generic_resume_md = outputs_dir / "tailored_resume.md"
    generic_cover_docx = outputs_dir / "tailored_cover_letter.docx"
    generic_cover_md = outputs_dir / "tailored_cover_letter.md"

    final_resume_docx = application_dir / f"{file_label}_resume.docx"
    final_resume_md = application_dir / f"{file_label}_resume.md"
    final_cover_docx = application_dir / f"{file_label}_cover_letter.docx"
    final_cover_md = application_dir / f"{file_label}_cover_letter.md"

    copy_if_exists(generic_resume_docx, final_resume_docx)
    copy_if_exists(generic_resume_md, final_resume_md)
    copy_if_exists(generic_cover_docx, final_cover_docx)
    copy_if_exists(generic_cover_md, final_cover_md)

    delete_if_exists(generic_resume_docx)
    delete_if_exists(generic_resume_md)
    delete_if_exists(generic_cover_docx)
    delete_if_exists(generic_cover_md)

    return {
        "resume_docx": final_resume_docx.name,
        "resume_md": final_resume_md.name,
        "cover_letter_docx": final_cover_docx.name,
        "cover_letter_md": final_cover_md.name,
    }

