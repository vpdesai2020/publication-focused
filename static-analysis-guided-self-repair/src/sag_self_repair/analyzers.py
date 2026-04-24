from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Sequence

from .schema import AnalyzerRun, ToolFinding


def run_command(command: Sequence[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(command),
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return subprocess.CompletedProcess(list(command), 127, "", str(exc))


def parse_bandit_json(payload: str) -> tuple[ToolFinding, ...]:
    data = _loads(payload)
    findings = []
    for item in data.get("results", []):
        findings.append(
            ToolFinding(
                tool="bandit",
                rule_id=str(item.get("test_id", "unknown")),
                message=str(item.get("issue_text", "")),
                path=str(item.get("filename", "")),
                line=_as_int(item.get("line_number")),
                severity=str(item.get("issue_severity", "")).lower() or None,
                cwe=_extract_cwe(item.get("issue_cwe")),
            )
        )
    return tuple(findings)


def parse_semgrep_json(payload: str) -> tuple[ToolFinding, ...]:
    data = _loads(payload)
    findings = []
    for item in data.get("results", []):
        extra = item.get("extra", {})
        metadata = extra.get("metadata", {})
        start = item.get("start", {})
        findings.append(
            ToolFinding(
                tool="semgrep",
                rule_id=str(item.get("check_id", "unknown")),
                message=str(extra.get("message", "")),
                path=str(item.get("path", "")),
                line=_as_int(start.get("line")),
                severity=str(extra.get("severity", "")).lower() or None,
                cwe=_extract_cwe(metadata.get("cwe")),
            )
        )
    return tuple(findings)


def parse_sarif(payload: str, tool_name: str = "codeql") -> tuple[ToolFinding, ...]:
    data = _loads(payload)
    findings = []
    for run in data.get("runs", []):
        rules = _rules_by_id(run)
        for result in run.get("results", []):
            rule_id = str(result.get("ruleId", "unknown"))
            location = _first_location(result)
            rule = rules.get(rule_id, {})
            findings.append(
                ToolFinding(
                    tool=tool_name,
                    rule_id=rule_id,
                    message=_message_text(result.get("message")) or _message_text(rule.get("shortDescription")),
                    path=location["path"],
                    line=location["line"],
                    severity=_sarif_severity(result, rule),
                    cwe=_extract_cwe(rule.get("properties", {}).get("tags")),
                )
            )
    return tuple(findings)


class StaticAnalyzerRunner:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def bandit(self, target: Path) -> AnalyzerRun:
        completed = run_command(["bandit", "-r", str(target), "-f", "json"], cwd=self.project_root)
        findings = parse_bandit_json(completed.stdout) if completed.stdout.strip() else ()
        return AnalyzerRun("bandit", completed.returncode, findings, error=completed.stderr.strip() or None)

    def semgrep(self, target: Path, config: Path | str = "auto") -> AnalyzerRun:
        completed = run_command(
            ["semgrep", "scan", "--json", "--config", str(config), str(target)],
            cwd=self.project_root,
        )
        findings = parse_semgrep_json(completed.stdout) if completed.stdout.strip() else ()
        return AnalyzerRun("semgrep", completed.returncode, findings, error=completed.stderr.strip() or None)

    def codeql_sarif_file(self, sarif_path: Path) -> AnalyzerRun:
        payload = sarif_path.read_text(encoding="utf-8")
        findings = parse_sarif(payload, tool_name="codeql")
        return AnalyzerRun("codeql", 0, findings, raw_output_path=str(sarif_path))


def _loads(payload: str) -> dict[str, Any]:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_cwe(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, int):
        return f"CWE-{value}"
    if isinstance(value, dict):
        return _extract_cwe(value.get("id") or value.get("name"))
    if isinstance(value, (list, tuple, set)):
        for item in value:
            extracted = _extract_cwe(item)
            if extracted:
                return extracted
        return None
    text = str(value).upper()
    if text.strip().isdigit():
        return f"CWE-{text.strip()}"
    marker = "CWE-"
    if marker not in text:
        return None
    start = text.find(marker)
    digits = []
    for char in text[start + len(marker) :]:
        if char.isdigit():
            digits.append(char)
        elif digits:
            break
    return f"CWE-{''.join(digits)}" if digits else None


def _rules_by_id(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    driver = run.get("tool", {}).get("driver", {})
    return {str(rule.get("id")): rule for rule in driver.get("rules", [])}


def _first_location(result: dict[str, Any]) -> dict[str, Any]:
    locations = result.get("locations", [])
    if not locations:
        return {"path": "", "line": None}
    physical = locations[0].get("physicalLocation", {})
    region = physical.get("region", {})
    artifact = physical.get("artifactLocation", {})
    return {
        "path": str(artifact.get("uri", "")),
        "line": _as_int(region.get("startLine")),
    }


def _message_text(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("text", ""))
    return str(message or "")


def _sarif_severity(result: dict[str, Any], rule: dict[str, Any]) -> str | None:
    level = result.get("level")
    if level:
        return str(level).lower()
    properties = rule.get("properties", {})
    severity = properties.get("security-severity") or properties.get("problem.severity")
    return str(severity).lower() if severity else None
