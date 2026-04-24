from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "task_id",
    "cwe",
    "variant",
    "tool",
    "rule_id",
    "severity",
    "finding_cwe",
    "path",
    "line",
    "message",
    "review_label",
    "review_notes",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a manual-review CSV from analyzer findings.")
    parser.add_argument(
        "--external-analyzers",
        type=Path,
        default=Path("outputs/analysis/external_analyzers.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/analysis/manual_review_sheet.csv"),
    )
    args = parser.parse_args()

    payload = json.loads(args.external_analyzers.read_text(encoding="utf-8"))
    rows = []
    for task_row in payload.get("rows", []):
        for analyzer in task_row.get("analyzers", []):
            for finding in analyzer.get("findings", []):
                rows.append(
                    {
                        "task_id": task_row["task_id"],
                        "cwe": task_row["cwe"],
                        "variant": task_row["variant"],
                        "tool": analyzer["tool"],
                        "rule_id": finding.get("rule_id"),
                        "severity": finding.get("severity"),
                        "finding_cwe": finding.get("cwe"),
                        "path": finding.get("path"),
                        "line": finding.get("line"),
                        "message": finding.get("message"),
                        "review_label": "",
                        "review_notes": "",
                    }
                )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()

