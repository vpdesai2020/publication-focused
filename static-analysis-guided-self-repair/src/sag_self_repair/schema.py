from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ToolFinding:
    tool: str
    rule_id: str
    message: str
    path: str
    line: int | None = None
    severity: str | None = None
    cwe: str | None = None

    @property
    def fingerprint(self) -> str:
        parts = [
            self.tool.lower(),
            self.rule_id.lower(),
            Path(self.path).as_posix().lower(),
            str(self.line or ""),
            (self.cwe or "").upper(),
        ]
        return "|".join(parts)

    def to_feedback(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "cwe": self.cwe,
            "path": self.path,
            "line": self.line,
            "message": self.message,
        }


@dataclass(frozen=True)
class AnalyzerRun:
    tool: str
    exit_code: int
    findings: tuple[ToolFinding, ...] = ()
    raw_output_path: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 or bool(self.findings)


@dataclass(frozen=True)
class TestRun:
    __test__ = False

    name: str
    exit_code: int
    kind: str = "functional"
    passed: int = 0
    failed: int = 0
    duration_seconds: float | None = None
    output: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and self.failed == 0

    @property
    def is_functional(self) -> bool:
        return self.kind == "functional"


@dataclass(frozen=True)
class RepairIteration:
    task_id: str
    iteration: int
    analyzer_runs: tuple[AnalyzerRun, ...] = ()
    test_runs: tuple[TestRun, ...] = ()
    patch: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def findings(self) -> tuple[ToolFinding, ...]:
        return tuple(
            finding
            for analyzer_run in self.analyzer_runs
            for finding in analyzer_run.findings
        )

    @property
    def tests_ok(self) -> bool:
        return bool(self.test_runs) and all(test_run.ok for test_run in self.test_runs)

    @property
    def functional_tests_ok(self) -> bool:
        functional_runs = tuple(test_run for test_run in self.test_runs if test_run.is_functional)
        return bool(functional_runs) and all(test_run.ok for test_run in functional_runs)
