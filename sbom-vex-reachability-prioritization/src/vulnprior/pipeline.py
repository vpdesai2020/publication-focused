from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .cvss import parse_cvss_base_score, severity_label
from .maven import MavenDependency, collect_maven_dependencies
from .models import Reachability, VexStatus, VulnerabilityFinding
from .osv_client import OsvPackageQuery, query_batch_chunked
from .ranker import rank_findings
from .reachability import classify_dependency_reachability
from .syft import SyftUnavailable, generate_syft_cyclonedx_maven_components


@dataclass(frozen=True, slots=True)
class PilotRepository:
    name: str
    url: str
    ref: str | None = None
    notes: str | None = None


def run_pilot(
    config_path: Path,
    workdir: Path,
    output_dir: Path,
    limit: int | None = None,
    sbom_backend: str = "auto",
    syft_bin: str = "syft",
) -> dict[str, Any]:
    repositories = _load_repositories(config_path)
    if limit is not None:
        repositories = repositories[:limit]

    workdir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    repo_workdir = workdir / "repositories"
    repo_workdir.mkdir(parents=True, exist_ok=True)

    all_findings: list[VulnerabilityFinding] = []
    repository_summaries = []
    failures = []

    for repository in repositories:
        try:
            repo_dir = _materialize_repository(repository, repo_workdir)
            repo_output = output_dir / "repositories" / repository.name
            repo_output.mkdir(parents=True, exist_ok=True)
            components, sbom_info = _collect_components(
                repo_dir=repo_dir,
                repo_output=repo_output,
                sbom_backend=sbom_backend,
                syft_bin=syft_bin,
            )
            repo_findings = _find_vulnerabilities(repository, repo_dir, components)
            repo_ranked = rank_findings(repo_findings)
            _write_repo_outputs(output_dir, repository, components, repo_findings, repo_ranked, sbom_info)
            all_findings.extend(repo_findings)
            repository_summaries.append(
                {
                    "name": repository.name,
                    "url": repository.url,
                    "ref": repository.ref,
                    "components": len(components),
                    "sbom_backend": sbom_info["backend"],
                    "sbom_path": sbom_info.get("sbom_path"),
                    "sbom_fallback_reason": sbom_info.get("fallback_reason"),
                    "vulnerability_findings": len(repo_findings),
                    "reachable_findings": sum(
                        1 for finding in repo_findings if finding.reachability == Reachability.REACHABLE
                    ),
                    "top_priority": repo_ranked[0].label if repo_ranked else None,
                }
            )
        except Exception as exc:  # Keep pilot runs moving across repository failures.
            failures.append({"name": repository.name, "url": repository.url, "error": str(exc)})

    ranked = rank_findings(all_findings)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path),
        "workdir": str(workdir),
        "output_dir": str(output_dir),
        "requested_sbom_backend": sbom_backend,
        "syft_bin": syft_bin,
        "repositories_requested": len(repositories),
        "repositories_completed": len(repository_summaries),
        "repositories_failed": len(failures),
        "component_count": sum(item["components"] for item in repository_summaries),
        "finding_count": len(all_findings),
        "reachable_finding_count": sum(
            1 for finding in all_findings if finding.reachability == Reachability.REACHABLE
        ),
        "priority_counts": _priority_counts(ranked),
        "repositories": repository_summaries,
        "failures": failures,
    }
    _write_aggregate_outputs(output_dir, all_findings, ranked, summary)
    return summary


def _load_repositories(config_path: Path) -> list[PilotRepository]:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    repositories = payload.get("repositories", payload)
    return [
        PilotRepository(
            name=item["name"],
            url=item["url"],
            ref=item.get("ref"),
            notes=item.get("notes"),
        )
        for item in repositories
    ]


def _materialize_repository(repository: PilotRepository, repo_workdir: Path) -> Path:
    repo_workdir = repo_workdir.resolve()
    repo_dir = (repo_workdir / repository.name).resolve()
    if not repo_dir.exists():
        _run(["git", "clone", "--depth", "1", repository.url, str(repo_dir)], repo_workdir)
    if repository.ref:
        _run(["git", "fetch", "--depth", "1", "origin", repository.ref], repo_dir)
        _run(["git", "checkout", "FETCH_HEAD"], repo_dir)
    return repo_dir


def _collect_components(
    repo_dir: Path,
    repo_output: Path,
    sbom_backend: str,
    syft_bin: str,
) -> tuple[list[MavenDependency], dict[str, Any]]:
    if sbom_backend not in {"auto", "syft", "maven"}:
        raise ValueError(f"Unsupported SBOM backend: {sbom_backend}")

    if sbom_backend in {"auto", "syft"}:
        sbom_path = repo_output / "sbom.cdx.json"
        try:
            result = generate_syft_cyclonedx_maven_components(repo_dir, sbom_path, syft_bin)
            return result.components, {
                "backend": "syft-cyclonedx",
                "sbom_path": str(sbom_path),
                "syft_version": result.version,
                "syft_command": result.command,
            }
        except SyftUnavailable as exc:
            if sbom_backend == "syft":
                raise
            fallback_reason = str(exc)
        except RuntimeError as exc:
            if sbom_backend == "syft":
                raise
            fallback_reason = str(exc)

        components = collect_maven_dependencies(repo_dir)
        return components, {
            "backend": "maven-pom",
            "fallback_reason": fallback_reason,
        }

    components = collect_maven_dependencies(repo_dir)
    return components, {"backend": "maven-pom"}


def _find_vulnerabilities(
    repository: PilotRepository,
    repo_dir: Path,
    components: list[MavenDependency],
) -> list[VulnerabilityFinding]:
    queries = [
        OsvPackageQuery(name=component.name, ecosystem="Maven", version=component.version)
        for component in components
    ]
    osv_results = query_batch_chunked(queries) if queries else []
    findings = []
    for component, osv_result in zip(components, osv_results):
        reachability = classify_dependency_reachability(repo_dir, component)
        for vulnerability in osv_result.get("vulns", []):
            cvss_score = _cvss_score(vulnerability)
            finding = VulnerabilityFinding(
                vulnerability_id=vulnerability.get("id", "UNKNOWN"),
                package=component.package_url,
                ecosystem="Maven",
                installed_version=component.version,
                severity=_severity(vulnerability, cvss_score),
                cvss_score=cvss_score,
                known_exploited=False,
                vex_status=VexStatus.UNKNOWN,
                reachability=reachability.state,
                reachable_paths=reachability.evidence,
                source=repository.name,
                metadata={
                    "repository_url": repository.url,
                    "repository_ref": repository.ref,
                    "package_name": component.name,
                    "aliases": vulnerability.get("aliases", []),
                    "summary": vulnerability.get("summary"),
                    "modified": vulnerability.get("modified"),
                    "published": vulnerability.get("published"),
                    "pom_path": component.pom_path,
                    "scope": component.scope,
                    "reachability_confidence": reachability.confidence,
                    "parser": component.parser,
                },
            )
            findings.append(finding)
    return findings


def _cvss_score(vulnerability: dict[str, Any]) -> float | None:
    for severity in vulnerability.get("severity", []):
        score = parse_cvss_base_score(severity.get("score"))
        if score is not None:
            return score
    database_specific = vulnerability.get("database_specific", {})
    nvd = database_specific.get("nvd_published_at")
    if isinstance(nvd, dict):
        return nvd.get("cvss_score")
    return None


def _severity(vulnerability: dict[str, Any], cvss_score: float | None) -> str | None:
    label = severity_label(cvss_score)
    if label:
        return label
    database_specific = vulnerability.get("database_specific", {})
    value = database_specific.get("severity")
    if isinstance(value, str):
        return value.lower()
    return None


def _write_repo_outputs(
    output_dir: Path,
    repository: PilotRepository,
    components: list[MavenDependency],
    findings: list[VulnerabilityFinding],
    ranked: list,
    sbom_info: dict[str, Any],
) -> None:
    repo_output = output_dir / "repositories" / repository.name
    repo_output.mkdir(parents=True, exist_ok=True)
    _write_json(repo_output / "sbom-info.json", sbom_info)
    _write_json(repo_output / "components.json", [component.to_dict() for component in components])
    _write_json(repo_output / "findings.json", [_finding_to_dict(finding) for finding in findings])
    _write_json(repo_output / "ranked.json", [item.to_dict() for item in ranked])


def _write_aggregate_outputs(
    output_dir: Path,
    findings: list[VulnerabilityFinding],
    ranked: list,
    summary: dict[str, Any],
) -> None:
    _write_json(output_dir / "pilot_summary.json", summary)
    _write_json(output_dir / "pilot_findings.json", [_finding_to_dict(finding) for finding in findings])
    _write_json(output_dir / "pilot_ranked.json", [item.to_dict() for item in ranked])
    _write_manual_label_template(output_dir / "manual-labels-template.csv", ranked)
    (output_dir / "pilot_summary.md").write_text(_summary_markdown(summary, ranked), encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_manual_label_template(path: Path, ranked: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "repository",
                "vulnerability_id",
                "package",
                "installed_version",
                "priority_score",
                "priority_label",
                "reachability",
                "human_label",
                "review_notes",
            ]
        )
        for item in ranked:
            finding = item.finding
            writer.writerow(
                [
                    finding.source,
                    finding.vulnerability_id,
                    finding.package,
                    finding.installed_version,
                    f"{item.score:.4f}",
                    item.label,
                    finding.reachability.value,
                    "",
                    "",
                ]
            )


def _summary_markdown(summary: dict[str, Any], ranked: list) -> str:
    lines = [
        "# Pilot Run Summary",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Repositories completed: `{summary['repositories_completed']}`",
        f"- Repositories failed: `{summary['repositories_failed']}`",
        f"- Requested SBOM backend: `{summary['requested_sbom_backend']}`",
        f"- Components extracted: `{summary['component_count']}`",
        f"- Vulnerability findings: `{summary['finding_count']}`",
        f"- Reachable findings: `{summary['reachable_finding_count']}`",
        f"- Priority counts: `{summary['priority_counts']}`",
        "",
        "## Repositories",
        "",
        "| Repository | SBOM Backend | Components | Findings | Reachable | Top Priority |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for repo in summary["repositories"]:
        lines.append(
            f"| {repo['name']} | {repo['sbom_backend']} | {repo['components']} | {repo['vulnerability_findings']} | "
            f"{repo['reachable_findings']} | {repo['top_priority'] or ''} |"
        )
    lines.extend(["", "## Top Findings", "", "| Rank | Repository | Vulnerability | Package | Score | Label | Reachability |", "| ---: | --- | --- | --- | ---: | --- | --- |"])
    for index, item in enumerate(ranked[:25], start=1):
        finding = item.finding
        lines.append(
            f"| {index} | {finding.source} | {finding.vulnerability_id} | "
            f"{finding.metadata.get('package_name', finding.package)} | {item.score:.4f} | "
            f"{item.label} | {finding.reachability.value} |"
        )
    if summary["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in summary["failures"]:
            lines.append(f"- `{failure['name']}`: {failure['error']}")
    lines.append("")
    return "\n".join(lines)


def _finding_to_dict(finding: VulnerabilityFinding) -> dict[str, Any]:
    return {
        "vulnerability_id": finding.vulnerability_id,
        "package": finding.package,
        "ecosystem": finding.ecosystem,
        "installed_version": finding.installed_version,
        "severity": finding.severity,
        "cvss_score": finding.cvss_score,
        "epss": finding.epss,
        "known_exploited": finding.known_exploited,
        "vex_status": finding.vex_status.value,
        "vex_justification": finding.vex_justification,
        "reachability": finding.reachability.value,
        "reachable_paths": finding.reachable_paths,
        "source": finding.source,
        "metadata": finding.metadata,
    }


def _priority_counts(ranked: list) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for item in ranked:
        counts[item.label] = counts.get(item.label, 0) + 1
    return counts


def _run(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
