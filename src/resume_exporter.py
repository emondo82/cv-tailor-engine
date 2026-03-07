def export_markdown(resume, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Tailored Resume\n\n")

        f.write("## Professional Summary\n\n")
        f.write(resume["summary"] + "\n\n")

        f.write("## Core Skills\n\n")
        f.write(" | ".join(resume["skills"]) + "\n\n")

        f.write("## Selected Experience\n\n")
        for project in resume["selected_projects"]:
            company = project.get("company") or "Unknown"
            role = project.get("role") or ""
            client = project.get("client") or ""

            header = company if not role else f"{company} — {role}"
            f.write(f"### {header}\n\n")

            if client:
                f.write(f"Client: {client}\n\n")

            for r in (project.get("responsibilities", []) or [])[:4]:
                f.write(f"- {r}\n")

            f.write("\n")

        f.write("## Education\n\n")
        for item in resume.get("education", []):
            degree = item.get("degree", "")
            field = item.get("field", "")
            institution = item.get("institution", "")
            start_date = item.get("start_date", "")
            end_date = item.get("end_date", "")

            line = degree
            if field:
                line += f" in {field}"
            if institution:
                line += f" — {institution}"
            if start_date or end_date:
                line += f" ({start_date} - {end_date})"

            f.write(f"- {line}\n")

        f.write("\n## Certifications\n\n")
        for cert in resume.get("certifications", []):
            name = cert.get("name", "")
            provider = cert.get("provider", "")
            date = cert.get("date", "")

            line = name
            if provider:
                line += f" — {provider}"
            if date:
                line += f" ({date})"

            f.write(f"- {line}\n")

        f.write("\n## Languages\n\n")
        for lang in resume.get("languages", []):
            language = lang.get("language", "")
            if lang.get("level"):
                f.write(f"- {language}: {lang['level']}\n")
            else:
                spoken = lang.get("spoken", "")
                written = lang.get("written", "")
                f.write(f"- {language}: Spoken {spoken}, Written {written}\n")