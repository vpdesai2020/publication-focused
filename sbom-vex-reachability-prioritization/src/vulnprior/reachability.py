from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .maven import MavenDependency
from .models import Reachability


SOURCE_SUFFIXES = {".java", ".kt"}


@dataclass(frozen=True, slots=True)
class ReachabilityResult:
    state: Reachability
    evidence: list[str]
    confidence: str


def classify_dependency_reachability(repo_path: Path, dependency: MavenDependency) -> ReachabilityResult:
    source_files = _source_files(repo_path)
    if not source_files:
        return ReachabilityResult(Reachability.UNKNOWN, [], "no_source_files")

    candidates = _namespace_candidates(dependency)
    if not candidates:
        return ReachabilityResult(Reachability.UNKNOWN, [], "no_namespace_candidates")

    evidence = []
    for source_file in source_files:
        try:
            text = source_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for candidate in candidates:
            if _candidate_is_referenced(candidate, text):
                evidence.append(f"{source_file.relative_to(repo_path)} references {candidate}")
                break
        if len(evidence) >= 5:
            break

    if evidence:
        return ReachabilityResult(Reachability.REACHABLE, evidence, "namespace_reference_observed")
    return ReachabilityResult(Reachability.UNREACHABLE, [], "namespace_not_observed_static_scan")


def _source_files(repo_path: Path) -> list[Path]:
    files = []
    for path in repo_path.rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if _is_ignored_path(path):
            continue
        files.append(path)
    return files


def _namespace_candidates(dependency: MavenDependency) -> list[str]:
    candidates = []
    group_id = dependency.group_id
    if _looks_like_namespace(group_id):
        candidates.append(group_id)
    artifact_tokens = [
        token
        for token in re.split(r"[-_.]", dependency.artifact_id)
        if token and token not in {"core", "api", "impl", "starter", "java", "client", "server"}
    ]
    if group_id and artifact_tokens:
        candidates.append(f"{group_id}.{artifact_tokens[0]}")
    return list(dict.fromkeys(candidates))


def _candidate_is_referenced(candidate: str, text: str) -> bool:
    return (
        f"import {candidate}" in text
        or f"from {candidate}" in text
        or f'"{candidate}' in text
        or f"'{candidate}" in text
        or f"{candidate}." in text
    )


def _looks_like_namespace(value: str) -> bool:
    return "." in value and not value.startswith("${") and "/" not in value


def _is_ignored_path(path: Path) -> bool:
    ignored = {".git", "target", "build", "out", ".gradle", ".mvn"}
    if any(part in ignored for part in path.parts):
        return True
    return "src" in path.parts and "test" in path.parts

