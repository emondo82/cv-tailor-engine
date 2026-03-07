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