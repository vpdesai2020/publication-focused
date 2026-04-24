from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair.analyzers import StaticAnalyzerRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run configured static analyzers and print normalized findings.")
    parser.add_argument("target", type=Path, help="File or directory to analyze.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--semgrep-config", default="configs/semgrep/python-security.yml")
    parser.add_argument("--skip-bandit", action="store_true")
    parser.add_argument("--skip-semgrep", action="store_true")
    args = parser.parse_args()

    runner = StaticAnalyzerRunner(args.project_root)
    runs = []
    if not args.skip_bandit:
        runs.append(runner.bandit(args.target))
    if not args.skip_semgrep:
        runs.append(runner.semgrep(args.target, args.semgrep_config))

    print(
        json.dumps(
            [
                {
                    "tool": run.tool,
                    "exit_code": run.exit_code,
                    "error": run.error,
                    "findings": [finding.to_feedback() for finding in run.findings],
                }
                for run in runs
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
