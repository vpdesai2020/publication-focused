from __future__ import annotations

import json

from .schema import RepairIteration


def build_repair_prompt(code: str, iteration: RepairIteration) -> str:
    feedback = {
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
            "Return a minimal patch only.",
            "Preserve the public API and intended behavior.",
            "Do not delete or weaken tests.",
            "Do not suppress static-analysis rules.",
            "Do not hard-code values only to satisfy tests.",
            "Prefer standard safe APIs over custom sanitizers.",
        ],
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
