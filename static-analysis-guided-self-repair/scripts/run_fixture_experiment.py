from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair.builtin_analyzer import analyze_python_file
from sag_self_repair.repair_prompt import build_repair_prompt
from sag_self_repair.results import TrialRecord
from sag_self_repair.schema import RepairIteration
from sag_self_repair.tasks import load_task_spec
from sag_self_repair.test_runner import run_pytest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a local fixture repair experiment without calling an LLM."
    )
    parser.add_argument(
        "--task-dir",
        type=Path,
        default=Path("tasks/python/py-cwe-078-command-injection"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/runs"))
    parser.add_argument("--strategy", choices=["identity", "fixture"], default="fixture")
    parser.add_argument("--model", default="fixture")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--repair-budget", type=int, default=1)
    args = parser.parse_args()
    task_dir = args.task_dir.resolve()
    output_dir = args.output_dir.resolve()

    task = load_task_spec(task_dir)
    run_dir = _new_run_dir(output_dir, task.id, args.strategy)
    workspace = run_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    shutil.copy2(task_dir / task.candidate_file, workspace / task.source_file)
    for relative_test in (*task.functional_tests, *task.security_tests):
        source = task_dir / relative_test
        destination = workspace / relative_test
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    before = _evaluate(task.id, 0, workspace, task.source_file, task.functional_tests, task.security_tests)
    prompt = build_repair_prompt((workspace / task.source_file).read_text(encoding="utf-8"), before)
    (run_dir / "repair_prompt.txt").write_text(prompt, encoding="utf-8")

    if args.strategy == "fixture":
        if not task.patched_file:
            raise SystemExit("Fixture strategy requires patched_file in task.json")
        shutil.copy2(task_dir / task.patched_file, workspace / task.source_file)

    after = _evaluate(task.id, 1, workspace, task.source_file, task.functional_tests, task.security_tests)
    record = TrialRecord(task_id=task.id, strategy=args.strategy, before=before, after=after)
    result = record.to_summary()
    result.update(
        {
            "model": args.model,
            "seed": args.seed,
            "repair_budget": args.repair_budget,
            "analyzers": ["builtin-python"],
            "manual_review_status": "not_reviewed",
        }
    )
    result["run_dir"] = str(run_dir)
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (run_dir / "iterations.json").write_text(
        json.dumps(
            {
                "before": _iteration_to_dict(before),
                "after": _iteration_to_dict(after),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


def _evaluate(
    task_id: str,
    iteration: int,
    workspace: Path,
    source_file: str,
    functional_tests: tuple[str, ...],
    security_tests: tuple[str, ...],
) -> RepairIteration:
    analyzer_run = analyze_python_file(workspace / source_file)
    test_runs = (
        run_pytest(functional_tests, cwd=workspace, kind="functional", name="pytest:functional"),
        run_pytest(security_tests, cwd=workspace, kind="security", name="pytest:security"),
    )
    return RepairIteration(
        task_id=task_id,
        iteration=iteration,
        analyzer_runs=(analyzer_run,),
        test_runs=test_runs,
    )


def _new_run_dir(output_dir: Path, task_id: str, strategy: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_id = "".join(part[0] for part in task_id.split("-") if part)[:10] or "task"
    for index in range(100):
        suffix = f"{stamp}-{short_id}-{strategy[:3]}-{index:02d}"
        run_dir = output_dir / suffix
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
            return run_dir
        except FileExistsError:
            continue
    raise RuntimeError("Could not create a unique run directory")


def _iteration_to_dict(iteration: RepairIteration) -> dict:
    return {
        "task_id": iteration.task_id,
        "iteration": iteration.iteration,
        "findings": [finding.to_feedback() for finding in iteration.findings],
        "tests": [
            {
                "name": test.name,
                "kind": test.kind,
                "exit_code": test.exit_code,
                "passed": test.passed,
                "failed": test.failed,
                "ok": test.ok,
                "output_tail": test.output[-2000:],
            }
            for test in iteration.test_runs
        ],
    }


if __name__ == "__main__":
    main()
