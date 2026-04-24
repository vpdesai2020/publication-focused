from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .repair_prompt import build_repair_prompt
from .schema import RepairIteration

PatchGenerator = Callable[[str], str]


@dataclass(frozen=True)
class RepairDecision:
    prompt: str
    patch: str
    should_continue: bool


def propose_patch(code: str, iteration: RepairIteration, generator: PatchGenerator) -> RepairDecision:
    prompt = build_repair_prompt(code, iteration)
    patch = generator(prompt)
    should_continue = bool(iteration.findings) or not iteration.tests_ok
    return RepairDecision(prompt=prompt, patch=patch, should_continue=should_continue)

