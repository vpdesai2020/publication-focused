from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ModelProvider(Protocol):
    name: str

    def generate_patch(self, prompt: str) -> str:
        """Return a patch or full replacement text from a repair prompt."""


@dataclass(frozen=True)
class FixtureProvider:
    name: str = "fixture"
    patch_path: Path | None = None

    def generate_patch(self, prompt: str) -> str:
        if self.patch_path is None:
            return ""
        return self.patch_path.read_text(encoding="utf-8")


@dataclass(frozen=True)
class CommandProvider:
    command: tuple[str, ...]
    name: str = "command-provider"
    timeout_seconds: int = 120

    def generate_patch(self, prompt: str) -> str:
        completed = subprocess.run(
            list(self.command),
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
            timeout=self.timeout_seconds,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "Model command failed")
        return completed.stdout

