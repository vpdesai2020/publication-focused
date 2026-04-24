from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fixture experiments over every task.json in a task root.")
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks/python"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/runs"))
    parser.add_argument(
        "--strategy",
        choices=["identity", "fixture", "both"],
        default="both",
    )
    args = parser.parse_args()

    strategies = ["identity", "fixture"] if args.strategy == "both" else [args.strategy]
    task_dirs = sorted(path.parent for path in args.tasks_root.rglob("task.json"))
    rows = []
    for task_dir in task_dirs:
        for strategy in strategies:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "scripts/run_fixture_experiment.py",
                    "--task-dir",
                    str(task_dir),
                    "--output-dir",
                    str(args.output_dir),
                    "--strategy",
                    strategy,
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                raise SystemExit(
                    f"Task run failed for {task_dir} / {strategy}\n"
                    f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
                )
            rows.append(json.loads(completed.stdout))
    print(json.dumps({"runs": len(rows), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()

