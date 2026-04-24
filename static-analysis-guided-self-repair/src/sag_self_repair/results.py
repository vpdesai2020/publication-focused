from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from .metrics import finding_delta, repair_success, vulnerability_reduction
from .schema import RepairIteration


@dataclass(frozen=True)
class TrialRecord:
    task_id: str
    strategy: str
    before: RepairIteration
    after: RepairIteration

    def to_summary(self) -> dict[str, Any]:
        delta = finding_delta(self.before, self.after)
        return {
            "task_id": self.task_id,
            "strategy": self.strategy,
            "findings_before": delta["before"],
            "findings_after": delta["after"],
            "findings_removed": delta["removed"],
            "findings_introduced": delta["introduced"],
            "vulnerability_reduction": vulnerability_reduction(delta["before"], delta["after"]),
            "functional_tests_before_ok": self.before.functional_tests_ok,
            "all_tests_after_ok": self.after.tests_ok,
            "repair_success": repair_success(self.before, self.after),
        }


def summarize_trials(records: list[TrialRecord]) -> dict[str, Any]:
    summaries = [record.to_summary() for record in records]
    if not summaries:
        return {
            "trials": 0,
            "repair_success_rate": 0.0,
            "mean_vulnerability_reduction": 0.0,
        }
    return {
        "trials": len(summaries),
        "repair_success_rate": mean(float(item["repair_success"]) for item in summaries),
        "mean_vulnerability_reduction": mean(item["vulnerability_reduction"] for item in summaries),
        "functional_preservation_rate": mean(float(item["all_tests_after_ok"]) for item in summaries),
        "summaries": summaries,
    }

