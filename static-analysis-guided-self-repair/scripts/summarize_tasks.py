from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair.tasks import load_task_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize task-pack composition.")
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks/python"))
    parser.add_argument("--csv-output", type=Path, default=Path("outputs/analysis/task_summary.csv"))
    parser.add_argument("--markdown-output", type=Path, default=Path("paper/task_summary.md"))
    args = parser.parse_args()

    tasks = [load_task_spec(path.parent) for path in sorted(args.tasks_root.rglob("task.json"))]
    cwe_counts = Counter(task.cwe for task in tasks)
    rows = [
        {
            "task_id": task.id,
            "language": task.language,
            "cwe": task.cwe,
            "functional_tests": len(task.functional_tests),
            "security_tests": len(task.security_tests),
        }
        for task in tasks
    ]
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    with args.csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    markdown = _markdown(cwe_counts, rows)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(json.dumps({"tasks": len(tasks), "cwes": dict(cwe_counts)}, indent=2))


def _markdown(cwe_counts: Counter, rows: list[dict]) -> str:
    lines = [
        "# Task Summary",
        "",
        "## CWE Coverage",
        "",
        "| CWE | Tasks |",
        "| --- | ---: |",
    ]
    for cwe, count in sorted(cwe_counts.items()):
        lines.append(f"| {cwe} | {count} |")
    lines.extend(
        [
            "",
            "## Tasks",
            "",
            "| Task | Language | CWE | Functional Test Files | Security Test Files |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['task_id']} | {row['language']} | {row['cwe']} | "
            f"{row['functional_tests']} | {row['security_tests']} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()

