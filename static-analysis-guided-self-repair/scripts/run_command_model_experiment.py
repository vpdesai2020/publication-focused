from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sag_self_repair.code_extract import extract_python_code
from sag_self_repair.experiment import (
    create_run_dir,
    evaluate_workspace,
    iteration_to_dict,
    prepare_workspace,
)
from sag_self_repair.repair_prompt import build_repair_prompt
from sag_self_repair.results import TrialRecord
from sag_self_repair.tasks import load_task_spec


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a repair experiment using a command-line model that reads prompt on stdin."
    )
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/model-runs"))
    parser.add_argument("--model", required=True)
    parser.add_argument("--repair-budget", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--analyzers", default="builtin")
    parser.add_argument("--semgrep-config", type=Path, default=Path("configs/semgrep/python-security.yml"))
    parser.add_argument("--model-command", nargs=argparse.REMAINDER, required=True)
    args = parser.parse_args()

    if not args.model_command:
        raise SystemExit("--model-command must be followed by an executable and arguments")

    task_dir = args.task_dir.resolve()
    output_dir = args.output_dir.resolve()
    task = load_task_spec(task_dir)
    strategy = "command_repair"
    run_dir = create_run_dir(output_dir, task.id, strategy)
    workspace = prepare_workspace(task_dir, task, run_dir)
    analyzers = tuple(item.strip() for item in args.analyzers.split(",") if item.strip())

    iterations = []
    before = evaluate_workspace(
        task,
        iteration=0,
        workspace=workspace,
        analyzers=analyzers,
        project_root=Path.cwd(),
        semgrep_config=args.semgrep_config,
    )
    iterations.append(before)

    current = before
    for iteration_number in range(1, args.repair_budget + 1):
        if current.tests_ok and not current.findings:
            break
        code = (workspace / task.source_file).read_text(encoding="utf-8")
        prompt = build_repair_prompt(code, current, response_format="full_file")
        prompt_path = run_dir / f"repair_prompt_{iteration_number}.txt"
        output_path = run_dir / f"model_output_{iteration_number}.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        model_output = _run_model(args.model_command, prompt)
        output_path.write_text(model_output, encoding="utf-8")
        replacement = extract_python_code(model_output)
        (workspace / task.source_file).write_text(replacement, encoding="utf-8")
        current = evaluate_workspace(
            task,
            iteration=iteration_number,
            workspace=workspace,
            analyzers=analyzers,
            project_root=Path.cwd(),
            semgrep_config=args.semgrep_config,
        )
        iterations.append(current)

    after = iterations[-1]
    result = TrialRecord(task.id, strategy, before, after).to_summary()
    result.update(
        {
            "model": args.model,
            "seed": args.seed,
            "repair_budget": args.repair_budget,
            "analyzers": list(analyzers),
            "manual_review_status": "not_reviewed",
            "run_dir": str(run_dir),
        }
    )
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (run_dir / "iterations.json").write_text(
        json.dumps([iteration_to_dict(iteration) for iteration in iterations], indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


def _run_model(command: list[str], prompt: str) -> str:
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Model command failed")
    return completed.stdout


if __name__ == "__main__":
    main()

