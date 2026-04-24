from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from .analyzers import StaticAnalyzerRunner
from .builtin_analyzer import analyze_python_file
from .schema import AnalyzerRun, RepairIteration
from .tasks import TaskSpec
from .test_runner import run_pytest


def create_run_dir(output_dir: Path, task_id: str, strategy: str) -> Path:
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


def prepare_workspace(task_dir: Path, task: TaskSpec, run_dir: Path) -> Path:
    workspace = run_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    shutil.copy2(task_dir / task.candidate_file, workspace / task.source_file)
    for relative_test in (*task.functional_tests, *task.security_tests):
        source = task_dir / relative_test
        destination = workspace / relative_test
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return workspace


def evaluate_workspace(
    task: TaskSpec,
    iteration: int,
    workspace: Path,
    analyzers: tuple[str, ...] = ("builtin",),
    project_root: Path | None = None,
    semgrep_config: Path | str = "configs/semgrep/python-security.yml",
) -> RepairIteration:
    source_path = workspace / task.source_file
    analyzer_runs = _run_analyzers(source_path, analyzers, project_root or Path.cwd(), semgrep_config)
    test_runs = (
        run_pytest(task.functional_tests, cwd=workspace, kind="functional", name="pytest:functional"),
        run_pytest(task.security_tests, cwd=workspace, kind="security", name="pytest:security"),
    )
    return RepairIteration(
        task_id=task.id,
        iteration=iteration,
        analyzer_runs=analyzer_runs,
        test_runs=test_runs,
    )


def iteration_to_dict(iteration: RepairIteration) -> dict:
    return {
        "task_id": iteration.task_id,
        "iteration": iteration.iteration,
        "findings": [finding.to_feedback() for finding in iteration.findings],
        "analyzer_runs": [
            {
                "tool": run.tool,
                "exit_code": run.exit_code,
                "error": run.error,
                "findings": [finding.to_feedback() for finding in run.findings],
            }
            for run in iteration.analyzer_runs
        ],
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


def _run_analyzers(
    source_path: Path,
    analyzers: tuple[str, ...],
    project_root: Path,
    semgrep_config: Path | str,
) -> tuple[AnalyzerRun, ...]:
    runner = StaticAnalyzerRunner(project_root)
    runs: list[AnalyzerRun] = []
    for analyzer in analyzers:
        if analyzer == "builtin":
            runs.append(analyze_python_file(source_path))
        elif analyzer == "bandit":
            runs.append(runner.bandit(source_path))
        elif analyzer == "semgrep":
            runs.append(runner.semgrep(source_path, semgrep_config))
        else:
            runs.append(AnalyzerRun(analyzer, 127, (), error=f"Unknown analyzer: {analyzer}"))
    return tuple(runs)

