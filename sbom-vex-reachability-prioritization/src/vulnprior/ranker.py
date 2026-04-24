from __future__ import annotations

from .models import RankedFinding, RankingWeights, Reachability, VexStatus, VulnerabilityFinding


SEVERITY_MAP = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "moderate": 0.5,
    "low": 0.25,
    "negligible": 0.05,
    "none": 0.0,
}


def rank_findings(
    findings: list[VulnerabilityFinding],
    weights: RankingWeights | None = None,
) -> list[RankedFinding]:
    active_weights = weights or RankingWeights()
    ranked = [score_finding(finding, active_weights) for finding in findings]
    return sorted(ranked, key=lambda item: item.score, reverse=True)


def score_finding(finding: VulnerabilityFinding, weights: RankingWeights) -> RankedFinding:
    severity_signal = _severity_signal(finding)
    exploit_signal = _exploit_signal(finding)
    reachability_signal = _reachability_signal(finding.reachability)
    vex_signal = _vex_signal(finding.vex_status)

    raw_score = (
        weights.severity * severity_signal
        + weights.exploit * exploit_signal
        + weights.reachability * reachability_signal
        + weights.vex * vex_signal
    )
    score = _apply_caps(raw_score, finding)
    return RankedFinding(
        finding=finding,
        score=score,
        label=_priority_label(score),
        rationale=_rationale(
            finding,
            severity_signal,
            exploit_signal,
            reachability_signal,
            vex_signal,
            raw_score,
            score,
        ),
    )


def _severity_signal(finding: VulnerabilityFinding) -> float:
    if finding.cvss_score is not None:
        return _clamp(finding.cvss_score / 10.0)
    if finding.severity:
        return SEVERITY_MAP.get(finding.severity.lower(), 0.4)
    return 0.4


def _exploit_signal(finding: VulnerabilityFinding) -> float:
    if finding.known_exploited:
        return 1.0
    if finding.epss is not None:
        return _clamp(finding.epss)
    return 0.35


def _reachability_signal(reachability: Reachability) -> float:
    return {
        Reachability.REACHABLE: 1.0,
        Reachability.MAYBE_REACHABLE: 0.65,
        Reachability.UNKNOWN: 0.45,
        Reachability.UNREACHABLE: 0.05,
    }[reachability]


def _vex_signal(status: VexStatus) -> float:
    return {
        VexStatus.AFFECTED: 1.0,
        VexStatus.UNDER_INVESTIGATION: 0.7,
        VexStatus.UNKNOWN: 0.55,
        VexStatus.FIXED: 0.2,
        VexStatus.NOT_AFFECTED: 0.05,
    }[status]


def _apply_caps(raw_score: float, finding: VulnerabilityFinding) -> float:
    score = raw_score
    if finding.vex_status == VexStatus.NOT_AFFECTED and finding.reachability != Reachability.REACHABLE:
        score = min(score, 0.25)
    if finding.reachability == Reachability.UNREACHABLE and not finding.known_exploited:
        score = min(score, 0.35)
    if finding.known_exploited and finding.reachability != Reachability.UNREACHABLE:
        score = max(score, 0.75)
    return _clamp(score)


def _priority_label(score: float) -> str:
    if score >= 0.75:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def _rationale(
    finding: VulnerabilityFinding,
    severity_signal: float,
    exploit_signal: float,
    reachability_signal: float,
    vex_signal: float,
    raw_score: float,
    final_score: float,
) -> list[str]:
    rationale = [
        f"severity_signal={severity_signal:.2f}",
        f"exploit_signal={exploit_signal:.2f}",
        f"reachability={finding.reachability.value}:{reachability_signal:.2f}",
        f"vex_status={finding.vex_status.value}:{vex_signal:.2f}",
    ]
    if final_score < raw_score:
        rationale.append(f"contextual_cap_applied={final_score:.2f}")
    if finding.known_exploited:
        rationale.append("known_exploited=true")
    if finding.reachable_paths:
        rationale.append(f"reachable_paths={len(finding.reachable_paths)}")
    return rationale


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

