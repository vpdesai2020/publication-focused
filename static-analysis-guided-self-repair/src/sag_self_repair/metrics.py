from __future__ import annotations

from .schema import RepairIteration, ToolFinding


def vulnerability_reduction(initial: int, final: int) -> float:
    return (initial - final) / max(initial, 1)


def unique_findings(findings: list[ToolFinding] | tuple[ToolFinding, ...]) -> set[str]:
    return {finding.fingerprint for finding in findings}


def finding_delta(before: RepairIteration, after: RepairIteration) -> dict[str, int]:
    before_set = unique_findings(before.findings)
    after_set = unique_findings(after.findings)
    return {
        "before": len(before_set),
        "after": len(after_set),
        "removed": len(before_set - after_set),
        "introduced": len(after_set - before_set),
    }


def repair_success(before: RepairIteration, after: RepairIteration) -> bool:
    delta = finding_delta(before, after)
    reduced = delta["after"] < delta["before"]
    return reduced and before.functional_tests_ok and after.tests_ok
