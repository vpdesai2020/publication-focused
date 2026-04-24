from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair.stats import mean, wilson_interval


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate fixture/run result.json files.")
    parser.add_argument("--results-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--csv-output", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    result_files = sorted(args.results_dir.rglob("result.json"))
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in result_files]
    if not rows:
        print(json.dumps({"trials": 0}, indent=2))
        return

    summary = {
        "trials": len(rows),
        "repair_success_rate": mean([float(row["repair_success"]) for row in rows]),
        "mean_vulnerability_reduction": mean([float(row["vulnerability_reduction"]) for row in rows]),
        "functional_preservation_rate": mean([float(row["all_tests_after_ok"]) for row in rows]),
        "by_strategy": _group(rows, "strategy"),
        "by_model": _group(rows, "model"),
        "rows": rows,
    }
    payload = json.dumps(summary, indent=2)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload, encoding="utf-8")
    if args.csv_output:
        args.csv_output.parent.mkdir(parents=True, exist_ok=True)
        _write_csv(args.csv_output, rows)
    print(payload)


def _group(rows: list[dict], key: str) -> dict[str, dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, "unknown"))].append(row)
    summary = {}
    for value, value_rows in grouped.items():
        successes = sum(1 for row in value_rows if row["repair_success"])
        lower, upper = wilson_interval(successes, len(value_rows))
        summary[value] = {
            "trials": len(value_rows),
            "repair_success_rate": successes / len(value_rows),
            "repair_success_ci95": [lower, upper],
            "mean_vulnerability_reduction": mean(
                [float(row["vulnerability_reduction"]) for row in value_rows]
            ),
            "functional_preservation_rate": mean(
                [float(row["all_tests_after_ok"]) for row in value_rows]
            ),
        }
    return summary


def _write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted({key for row in rows for key in row.keys() if key != "run_dir"})
    fieldnames.append("run_dir")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
