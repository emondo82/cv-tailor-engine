# CV Tailor Engine

A local Python-based CV tailoring engine that transforms detailed resume source documents into a structured knowledge base, matches them against a target job description, and generates a tailored resume and cover letter in Markdown and DOCX.

## Current Features

- Parse detailed CV source documents from DOCX
- Build a structured resume knowledge base
- Match experience against a job description
- Detect company/application style
- Extract JD-driven skills
- Prioritize the most relevant projects
- Prioritize the most relevant bullets within each project
- Generate a tailored resume in Markdown and DOCX
- Generate a tailored cover letter in Markdown and DOCX

## Project Structure

```text
cv-tailor-engine/
│
├── inputs/
│   ├── Master Resume.docx
│   ├── EC Format CV.docx
│   └── job_description.txt
│
├── outputs/
│   ├── resume_knowledge_base.json
│   ├── tailored_resume.md
│   ├── tailored_resume.docx
│   ├── tailored_cover_letter.md
│   └── tailored_cover_letter.docx
│
├── src/
│   ├── main.py
│   ├── parser.py
│   ├── models.py
│   ├── exporter.py
│   ├── job_matcher.py
│   ├── jd_skill_extractor.py
│   ├── style_classifier.py
│   ├── resume_builder.py
│   ├── resume_exporter.py
│   ├── docx_exporter.py
│   ├── cover_letter_builder.py
│   └── cover_letter_exporter.py
│
├── .gitignore
├── requirements.txt
└── README.md

How It Works
Resume pipeline
Master CV + EC CV
        ↓
parser.py
        ↓
resume_knowledge_base.json
        ↓
job_matcher.py
        ↓
resume_builder.py
        ↓
tailored_resume.md / tailored_resume.docx
Cover letter pipeline
resume_knowledge_base.json + job_description.txt
        ↓
cover_letter_builder.py
        ↓
tailored_cover_letter.md / tailored_cover_letter.docx
Setup

Create and activate a virtual environment:

python -m venv .venv
.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
Usage
1. Build the knowledge base
python src/main.py
2. Generate tailored resume
python src/resume_builder.py
3. Generate tailored cover letter
python src/cover_letter_builder.py
Notes

The engine is evidence-based and uses the detailed EC-format CV as the source of truth.

The Master Resume is mainly used as a narrative/profile source.

Inputs and outputs are excluded from version control by default.

Planned Improvements

One-command application pipeline

More visible style-based resume templates

Skill-aware bullet rewriting

Improved company/job-title extraction

Optional semantic matching

---

## 2. Check `.gitignore`

Make sure your `.gitignore` contains this:

```gitignore
.venv/
__pycache__/
*.pyc
outputs/
.env
inputs/

That keeps:

personal source files out

generated outputs out

virtual env out

3. Check git status

Run:

git status

You should see your updated code files and README changes.

4. Add everything
git add .
5. Commit with a proper message

Use this:

git commit -m "Enhance CV tailoring engine with style detection, JD skill extraction, bullet prioritization, and cover letter export"
6. Push to GitHub
git push

Because your remote is already configured, git push should be enough.