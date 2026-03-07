from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None

    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)
    return backup_path


def restore_file(backup_path: Path | None, target_path: Path) -> None:
    if backup_path and backup_path.exists():
        shutil.copy2(backup_path, target_path)
        backup_path.unlink(missing_ok=True)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    src_dir = project_root / "src"
    inputs_dir = project_root / "inputs"
    batch_dir = inputs_dir / "job_descriptions"
    main_jd_path = inputs_dir / "job_description.txt"
    apply_script = src_dir / "apply.py"

    if not batch_dir.exists():
        raise FileNotFoundError(f"Missing batch folder: {batch_dir}")

    if not apply_script.exists():
        raise FileNotFoundError(f"Missing apply script: {apply_script}")

    jd_files = sorted(batch_dir.glob("*.txt"))
    if not jd_files:
        raise FileNotFoundError(f"No .txt job descriptions found in: {batch_dir}")

    backup_path = backup_file(main_jd_path)

    results: list[tuple[str, str]] = []

    print("CV Tailor Engine — Batch Apply Mode")
    print(f"Found {len(jd_files)} job descriptions.")
    print(f"Batch source folder: {batch_dir}")
    print()

    try:
        for index, jd_file in enumerate(jd_files, start=1):
            print(f"=== [{index}/{len(jd_files)}] Processing: {jd_file.name} ===")

            shutil.copy2(jd_file, main_jd_path)

            result = subprocess.run(
                [sys.executable, str(apply_script)],
                check=False,
            )

            if result.returncode == 0:
                print(f"SUCCESS: {jd_file.name}\n")
                results.append((jd_file.name, "SUCCESS"))
            else:
                print(f"FAILED: {jd_file.name} (exit code {result.returncode})\n")
                results.append((jd_file.name, f"FAILED ({result.returncode})"))

    finally:
        restore_file(backup_path, main_jd_path)

    print("=== Batch run summary ===")
    for file_name, status in results:
        print(f"{file_name}: {status}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = project_root / "outputs" / f"batch_summary_{timestamp}.txt"
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    summary_lines = [
        "CV Tailor Engine — Batch Apply Summary",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    summary_lines.extend([f"{file_name}: {status}" for file_name, status in results])

    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print()
    print(f"Summary written to: {summary_path}")


if __name__ == "__main__":
    main()