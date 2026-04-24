from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TaskSpec:
    id: str
    language: str
    cwe: str
    prompt: str
    source_file: str = "solution.py"
    candidate_file: str = "candidate.py"
    patched_file: str | None = None
    functional_tests: tuple[str, ...] = ("tests/test_functionality.py",)
    security_tests: tuple[str, ...] = ("tests/test_security_properties.py",)

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "TaskSpec":
        return cls(
            id=str(mapping["id"]),
            language=str(mapping["language"]),
            cwe=str(mapping["cwe"]),
            prompt=str(mapping["prompt"]),
            source_file=str(mapping.get("source_file", "solution.py")),
            candidate_file=str(mapping.get("candidate_file", "candidate.py")),
            patched_file=(
                str(mapping["patched_file"])
                if mapping.get("patched_file") is not None
                else None
            ),
            functional_tests=tuple(mapping.get("functional_tests", ["tests/test_functionality.py"])),
            security_tests=tuple(mapping.get("security_tests", ["tests/test_security_properties.py"])),
        )


def load_task_spec(task_dir: Path) -> TaskSpec:
    task_path = task_dir / "task.json"
    return TaskSpec.from_mapping(json.loads(task_path.read_text(encoding="utf-8")))


def load_jsonl_tasks(path: Path) -> list[dict[str, Any]]:
    tasks = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            tasks.append(json.loads(stripped))
    return tasks

