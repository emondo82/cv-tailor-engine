from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

from pipeline.jd_stage import load_job_text, analyse_job_description
from pipeline.match_stage import run_match_stage
from pipeline.ats_stage import run_ats_stage
from pipeline.package_stage import build_file_label, package_outputs
from pipeline.metadata_stage import write_run_metadata
from resume_builder import build_resume
from llm_resume_enhancer import enhance_resume_versions


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"Created: {path}")


def run_step(script_path: Path, step_name: str) -> None:
    print(f"\n=== {step_name} ===")
    result = subprocess.run([sys.executable, str(script_path)], check=False)

    if result.returncode != 0:
        raise RuntimeError(
            f"{step_name} failed with exit code {result.returncode}: {script_path.name}"
        )


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src"
    inputs_dir = project_root / "inputs"
    outputs_dir = project_root / "outputs"

    parser_script = src_dir / "parser.py"
    resume_script = src_dir / "resume_builder.py"
    cover_letter_script = src_dir / "cover_letter_builder.py"

    job_description_path = inputs_dir / "job_description.txt"
    kb_path = outputs_dir / "resume_knowledge_base.json"
    base_resume_md_path = outputs_dir / "tailored_resume.md"

    candidate_name = "Tamas Kosina"

    if not parser_script.exists():
        raise FileNotFoundError(f"Missing parser script: {parser_script}")
    if not resume_script.exists():
        raise FileNotFoundError(f"Missing resume builder script: {resume_script}")
    if not cover_letter_script.exists():
        raise FileNotFoundError(f"Missing cover letter builder script: {cover_letter_script}")
    if not job_description_path.exists():
        raise FileNotFoundError(f"Missing job description file: {job_description_path}")

    outputs_dir.mkdir(parents=True, exist_ok=True)

    job_text = load_job_text(job_description_path)
    jd_analysis = analyse_job_description(job_text)

    company_name = jd_analysis["company_name"]
    job_title = jd_analysis["job_title"]
    jd_skills = jd_analysis["jd_skills"]
    application_slug = jd_analysis["application_slug"]

    application_dir = outputs_dir / application_slug
    application_dir.mkdir(parents=True, exist_ok=True)

    print("CV Tailor Engine — Application Package Generator")
    print(f"Project root: {project_root}")
    print(f"Detected company: {company_name}")
    print(f"Detected job title: {job_title}")
    print(f"Application folder: {application_dir}")

    run_step(parser_script, "Step 1/3 - Build resume knowledge base")
    run_step(resume_script, "Step 2/3 - Generate tailored resume")
    run_step(cover_letter_script, "Step 3/3 - Generate tailored cover letter")

    if not kb_path.exists():
        raise FileNotFoundError(f"Missing knowledge base file: {kb_path}")

    kb = load_json(kb_path)

    match_result = run_match_stage(kb, job_text, jd_skills, top_n=6)

    resume = build_resume(kb, job_text)

    ats_result = run_ats_stage(
        outputs_dir=outputs_dir,
        job_name=application_slug,
        jd_skills=jd_skills,
        source_projects=match_result["top_projects"],
        resume=resume,
    )
    ats_coverage = ats_result["ats_coverage"]

    file_label = build_file_label(
        job_title=job_title,
        candidate_name=candidate_name,
    )

    if not base_resume_md_path.exists():
        raise FileNotFoundError(f"Missing base resume markdown: {base_resume_md_path}")

    base_resume_markdown = read_text(base_resume_md_path)

    enhanced_versions = enhance_resume_versions(
    resume_markdown=base_resume_markdown,
    job_title=job_title,
    jd_skills=jd_skills,
    company_style=resume.get("style", {}).get("style", "general"),
    )

    resume_base_md_path = application_dir / "resume_base.md"
    resume_openai_md_path = application_dir / "resume_openai.md"
    resume_gemini_md_path = application_dir / "resume_gemini.md"

    write_text(resume_base_md_path, enhanced_versions["base"])
    write_text(resume_openai_md_path, enhanced_versions["openai"])
    write_text(resume_gemini_md_path, enhanced_versions["gemini"])

    packaged_files["resume_base_md"] = resume_base_md_path.name
    packaged_files["resume_openai_md"] = resume_openai_md_path.name
    packaged_files["resume_gemini_md"] = resume_gemini_md_path.name

    packaged_files = package_outputs(
        outputs_dir=outputs_dir,
        application_dir=application_dir,
        file_label=file_label,
    )


    write_run_metadata(
        output_dir=application_dir,
        company_name=company_name,
        job_title=job_title,
        output_slug=application_slug,
        jd_skills=jd_skills,
        project_matches=match_result["project_matches"],
        ats_coverage=ats_coverage,
        files=packaged_files,
    )

    print("\n=== Done ===")
    print("Generated application package:")
    for file_name in packaged_files.values():
        print(f"- {application_dir / file_name}")
    print(f"- {application_dir / 'run_metadata.json'}")
    print(f"- {ats_result['report_md_path']}")
    print(f"- {ats_result['report_json_path']}")


if __name__ == "__main__":
    main()