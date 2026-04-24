from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path
from typing import Sequence

from .schema import TestRun


def run_pytest(
    targets: Sequence[str] | None = None,
    cwd: Path | None = None,
    kind: str = "functional",
    name: str | None = None,
) -> TestRun:
    command = ["python", "-m", "pytest", "-q", *(targets or [])]
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    duration = time.monotonic() - started
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
    passed, failed = _parse_pytest_counts(output)
    return TestRun(
        name=name or "pytest",
        exit_code=completed.returncode,
        kind=kind,
        passed=passed,
        failed=failed,
        duration_seconds=duration,
        output=output,
    )


def _parse_pytest_counts(output: str) -> tuple[int, int]:
    passed = _first_count(r"(\d+) passed", output)
    failed = _first_count(r"(\d+) failed", output)
    errors = _first_count(r"(\d+) error", output)
    return passed, failed + errors


def _first_count(pattern: str, text: str) -> int:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0
