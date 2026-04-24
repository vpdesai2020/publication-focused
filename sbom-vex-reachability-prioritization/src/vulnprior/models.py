from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VexStatus(str, Enum):
    AFFECTED = "affected"
    NOT_AFFECTED = "not_affected"
    FIXED = "fixed"
    UNDER_INVESTIGATION = "under_investigation"
    UNKNOWN = "unknown"


class Reachability(str, Enum):
    REACHABLE = "reachable"
    MAYBE_REACHABLE = "maybe_reachable"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class VulnerabilityFinding:
    vulnerability_id: str
    package: str
    ecosystem: str | None = None
    installed_version: str | None = None
    severity: str | None = None
    cvss_score: float | None = None
    epss: float | None = None
    known_exploited: bool = False
    vex_status: VexStatus = VexStatus.UNKNOWN
    vex_justification: str | None = None
    reachability: Reachability = Reachability.UNKNOWN
    reachable_paths: list[str] = field(default_factory=list)
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RankingWeights:
    severity: float = 0.35
    exploit: float = 0.20
    reachability: float = 0.30
    vex: float = 0.15


@dataclass(slots=True)
class RankedFinding:
    finding: VulnerabilityFinding
    score: float
    label: str
    rationale: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vulnerability_id": self.finding.vulnerability_id,
            "package": self.finding.package,
            "ecosystem": self.finding.ecosystem,
            "installed_version": self.finding.installed_version,
            "severity": self.finding.severity,
            "cvss_score": self.finding.cvss_score,
            "epss": self.finding.epss,
            "known_exploited": self.finding.known_exploited,
            "vex_status": self.finding.vex_status.value,
            "vex_justification": self.finding.vex_justification,
            "reachability": self.finding.reachability.value,
            "reachable_paths": self.finding.reachable_paths,
            "priority_score": round(self.score, 4),
            "priority_label": self.label,
            "rationale": self.rationale,
            "source": self.finding.source,
            "metadata": self.finding.metadata,
        }

