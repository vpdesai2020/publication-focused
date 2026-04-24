from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair.analyzers import StaticAnalyzerRunner
from sag_self_repair.tasks import load_task_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bandit and Semgrep over candidate and fixture-patched tasks.")
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks/python"))
    parser.add_argument("--output", type=Path, default=Path("outputs/analysis/external_analyzers.json"))
    parser.add_argument("--semgrep-config", type=Path, default=Path("configs/semgrep/python-security.yml"))
    args = parser.parse_args()

    runner = StaticAnalyzerRunner(Path.cwd())
    rows = []
    for task_json in sorted(args.tasks_root.rglob("task.json")):
        task_dir = task_json.parent
        task = load_task_spec(task_dir)
        variants = [("candidate", task.candidate_file)]
        if task.patched_file:
            variants.append(("patched", task.patched_file))
        for variant, filename in variants:
            target = task_dir / filename
            analyzer_runs = [
                runner.bandit(target),
                runner.semgrep(target, args.semgrep_config),
            ]
            rows.append(
                {
                    "task_id": task.id,
                    "cwe": task.cwe,
                    "variant": variant,
                    "file": str(target),
                    "analyzers": [
                        {
                            "tool": run.tool,
                            "exit_code": run.exit_code,
                            "error": run.error,
                            "findings": [finding.to_feedback() for finding in run.findings],
                        }
                        for run in analyzer_runs
                    ],
                }
            )

    payload = {"rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

