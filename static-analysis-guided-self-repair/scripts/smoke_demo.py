from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair import AnalyzerRun, RepairIteration, TestRun, ToolFinding
from sag_self_repair.metrics import finding_delta, repair_success, vulnerability_reduction
from sag_self_repair.repair_prompt import build_repair_prompt


def main() -> None:
    before = RepairIteration(
        task_id="py-cwe-078-command-injection",
        iteration=0,
        analyzer_runs=(
            AnalyzerRun(
                tool="semgrep",
                exit_code=1,
                findings=(
                    ToolFinding(
                        tool="semgrep",
                        rule_id="python.subprocess.shell-true",
                        message="Avoid shell=True with untrusted input.",
                        path="solution.py",
                        line=7,
                        severity="error",
                        cwe="CWE-078",
                    ),
                ),
            ),
        ),
        test_runs=(TestRun(name="pytest", exit_code=0, passed=5, failed=0),),
    )
    after = RepairIteration(
        task_id="py-cwe-078-command-injection",
        iteration=1,
        analyzer_runs=(AnalyzerRun(tool="semgrep", exit_code=0, findings=()),),
        test_runs=(TestRun(name="pytest", exit_code=0, passed=5, failed=0),),
    )
    delta = finding_delta(before, after)
    prompt = build_repair_prompt("subprocess.check_output(cmd, shell=True)", before)
    print("delta=", delta)
    print("vulnerability_reduction=", vulnerability_reduction(delta["before"], delta["after"]))
    print("repair_success=", repair_success(before, after))
    print("prompt_preview=", prompt[:220].replace("\n", " "))


if __name__ == "__main__":
    main()
