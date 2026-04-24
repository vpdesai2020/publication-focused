from __future__ import annotations

import json

from .schema import RepairIteration


def build_repair_prompt(code: str, iteration: RepairIteration, response_format: str = "patch") -> str:
    if response_format not in {"patch", "full_file"}:
        raise ValueError("response_format must be 'patch' or 'full_file'")
    if response_format == "full_file":
        return _build_full_file_repair_prompt(code, iteration)
    return _build_patch_repair_prompt(code, iteration)


def _feedback(iteration: RepairIteration) -> dict:
    return {
        "task_id": iteration.task_id,
        "iteration": iteration.iteration,
        "static_findings": [finding.to_feedback() for finding in iteration.findings],
        "test_results": [
            {
                "name": test_run.name,
                "kind": test_run.kind,
                "ok": test_run.ok,
                "passed": test_run.passed,
                "failed": test_run.failed,
                "output_tail": test_run.output[-1200:],
            }
            for test_run in iteration.test_runs
        ],
        "constraints": [
            "Preserve the public API and intended behavior.",
            "Do not delete or weaken tests.",
            "Do not suppress static-analysis rules.",
            "Do not hard-code values only to satisfy tests.",
            "Prefer standard safe APIs over custom sanitizers.",
        ],
    }


def _build_patch_repair_prompt(code: str, iteration: RepairIteration) -> str:
    feedback = {
        **_feedback(iteration),
        "response_format": "Return a minimal patch only.",
    }
    return (
        "You are repairing LLM-generated code using tool evidence.\n"
        "Use the structured feedback to produce the smallest behavior-preserving security patch.\n\n"
        "STRUCTURED_FEEDBACK:\n"
        f"{json.dumps(feedback, indent=2, sort_keys=True)}\n\n"
        "CURRENT_CODE:\n"
        "```python\n"
        f"{code}\n"
        "```\n"
    )


def _build_full_file_repair_prompt(code: str, iteration: RepairIteration) -> str:
    feedback = {
        **_feedback(iteration),
        "response_format": (
            "Return exactly one complete replacement Python file. "
            "Use a single ```python fenced block and no explanatory prose."
        ),
    }
    return (
        "You are repairing LLM-generated code using tool evidence.\n"
        "Use the structured feedback to produce the smallest behavior-preserving security repair.\n\n"
        "STRUCTURED_FEEDBACK:\n"
        f"{json.dumps(feedback, indent=2, sort_keys=True)}\n\n"
        "CURRENT_CODE:\n"
        "```python\n"
        f"{code}\n"
        "```\n"
    )
