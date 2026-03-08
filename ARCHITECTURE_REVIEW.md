# Architecture Review

## Repository Structure Overview

```text
cv-tailor-engine/
|- inputs/
|  |- Master Resume.docx
|  |- EC Format CV.docx
|  |- job_description.txt
|  `- job_descriptions/                # batch JD inputs
|- outputs/
|  |- resume_knowledge_base.json
|  `- <application_slug>/              # packaged application outputs + run_metadata.json
|- src/
|  |- apply.py                         # end-to-end single application pipeline
|  |- apply_all.py                     # batch orchestration over multiple JDs
|  |- main.py                          # knowledge-base generation entrypoint
|  |- parser.py                        # DOCX parsing -> structured KB
|  |- models.py                        # pydantic schemas
|  |- job_matcher.py                   # project ranking against JD
|  |- resume_builder.py                # tailored resume assembly
|  |- cover_letter_builder.py          # tailored cover letter assembly
|  |- bullet_scorer.py                 # responsibility bullet relevance scoring
|  |- bullet_refiner.py                # deterministic bullet rewriting/cleanup
|  |- safe_llm_refiner.py              # optional LLM rewrite with safety checks
|  |- jd_skill_extractor.py            # JD skills extraction
|  |- project_evidence.py              # matched-skill evidence per project
|  |- ats_coverage.py                  # shared ATS normalization/matching helpers
|  |- resume_exporter.py               # resume markdown export
|  |- docx_exporter.py                 # resume DOCX export
|  |- cover_letter_exporter.py         # cover letter DOCX export
|  |- style_classifier.py              # company/style detection
|  |- exporter.py                      # KB JSON export
|  `- pipeline/
|     |- jd_stage.py                   # JD load + company/title/skills extraction
|     |- match_stage.py                # top project selection + evidence extraction
|     |- ats_stage.py                  # ATS coverage + keyword evidence report generation
|     |- package_stage.py              # output copy/rename/cleanup
|     `- metadata_stage.py             # run_metadata.json generation
|- README.md
`- requirements.txt
```

## Pipeline Execution Flow (JD -> Tailored Resume)

Primary end-to-end path is `src/apply.py`:

1. Load `inputs/job_description.txt` (`pipeline/jd_stage.load_job_text`).
2. Analyze JD (`pipeline/jd_stage.analyse_job_description`):
   - infer company
   - infer job title
   - extract JD skills (`jd_skill_extractor.extract_jd_skills`)
   - build application slug
3. Build/refresh KB by running `src/parser.py` subprocess:
   - reads `Master Resume.docx` + `EC Format CV.docx`
   - writes `outputs/resume_knowledge_base.json`
4. Generate resume by running `src/resume_builder.py` subprocess:
   - ranks projects against JD (`job_matcher.match_projects`)
   - selects top projects
   - prioritizes project bullets
   - refines bullets
   - builds summary/skills/style
   - exports `outputs/tailored_resume.md` + `outputs/tailored_resume.docx`
5. Generate cover letter by running `src/cover_letter_builder.py` subprocess.
6. Post-generation in-process steps in `apply.py`:
   - load KB JSON
   - run match stage for metadata evidence (`pipeline/match_stage.run_match_stage`)
   - rebuild resume object (`resume_builder.build_resume`)
   - run ATS stage (`pipeline/ats_stage.run_ats_stage`) to compute coverage and generate:
     - `outputs/<application_slug>_ats_report.md`
     - `outputs/<application_slug>_ats_report.json`
   - package files into `outputs/<application_slug>/` (`pipeline/package_stage.package_outputs`)
   - write `run_metadata.json` (`pipeline/metadata_stage.write_run_metadata`)

Batch mode `src/apply_all.py` loops through `inputs/job_descriptions/*.txt` and invokes `apply.py` per JD.

## Key Modules and Responsibilities

- `src/parser.py`: Extracts profile, education, certifications, languages, and project experience from source DOCX files.
- `src/models.py`: Defines structured data contracts for KB entities.
- `src/job_matcher.py`: Scores and ranks projects for JD relevance.
- `src/jd_skill_extractor.py`: Finds normalized JD skill signals.
- `src/resume_builder.py`: Core resume tailoring logic (selection, prioritization, rewriting, assembly).
- `src/bullet_scorer.py`: Numeric scoring of each responsibility bullet using JD skills/domain/tech/action terms.
- `src/bullet_refiner.py`: Deterministic bullet rewrite/cleanup with guardrails.
- `src/safe_llm_refiner.py`: Optional LLM rewrite + validator fallback path.
- `src/ats_coverage.py`: Shared ATS helpers (alias search terms + resume text normalization).
- `src/pipeline/ats_stage.py`: ATS matching stage with keyword evidence mapping and report export.
- `src/pipeline/*.py`: Orchestration helpers for JD analysis, matching evidence, packaging, and run metadata.
- `src/resume_exporter.py`, `src/docx_exporter.py`, `src/cover_letter_exporter.py`: Output format generation.

## Where Scoring, Prioritization, and Rewriting Occur

- **Project scoring/ranking**: `src/job_matcher.py`
  - `score_project(...)`
  - `match_projects(...)`

- **Bullet scoring**: `src/bullet_scorer.py`
  - `score_bullet(...)`

- **Bullet prioritization (top bullets per project)**: `src/resume_builder.py`
  - `prioritize_project_bullets(...)` scores each responsibility and keeps highest-ranked unique bullets.

- **Bullet rewriting/refinement**:
  - deterministic path: `src/bullet_refiner.py` (`refine_bullet`, `refine_bullets`)
  - optional guarded LLM path: `src/safe_llm_refiner.py` (OpenAI rewrite + Gemini safety validation)

## ATS Stage Placement (Implemented)

ATS coverage/reporting is implemented in `src/pipeline/ats_stage.py` and invoked from `src/apply.py` right after `build_resume(...)`, before packaging and metadata output.
