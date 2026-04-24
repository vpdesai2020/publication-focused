from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import Reachability, VexStatus, VulnerabilityFinding
from .pipeline import run_pilot
from .ranker import rank_findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank vulnerability findings with SBOM, VEX, and reachability context.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    rank_parser = subparsers.add_parser("rank", help="Rank normalized vulnerability findings.")
    rank_parser.add_argument("findings", type=Path, help="Input JSON list of normalized findings.")
    rank_parser.add_argument("--out", type=Path, help="Output JSON file. Prints to stdout when omitted.")

    pilot_parser = subparsers.add_parser("pilot", help="Run the Java/Maven pilot data pipeline.")
    pilot_parser.add_argument("--config", type=Path, default=Path("data/pilot_repositories.json"))
    pilot_parser.add_argument("--workdir", type=Path, default=Path("artifacts/pilot"))
    pilot_parser.add_argument("--out", type=Path, default=Path("data/pilot-latest"))
    pilot_parser.add_argument("--limit", type=int, help="Optional maximum number of repositories to process.")
    pilot_parser.add_argument(
        "--sbom-backend",
        choices=["auto", "syft", "maven"],
        default="auto",
        help="SBOM source: auto tries Syft CycloneDX first, syft requires Syft, maven uses the built-in parser.",
    )
    pilot_parser.add_argument("--syft-bin", default="syft", help="Path or command name for the Syft executable.")

    args = parser.parse_args()
    if args.command == "rank":
        _rank(args.findings, args.out)
    elif args.command == "pilot":
        summary = run_pilot(args.config, args.workdir, args.out, args.limit, args.sbom_backend, args.syft_bin)
        print(json.dumps(summary, indent=2))


def _rank(input_path: Path, output_path: Path | None) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    findings = [_finding_from_dict(item) for item in payload]
    ranked = [item.to_dict() for item in rank_findings(findings)]
    output = json.dumps(ranked, indent=2)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


def _finding_from_dict(item: dict[str, Any]) -> VulnerabilityFinding:
    return VulnerabilityFinding(
        vulnerability_id=item["vulnerability_id"],
        package=item["package"],
        ecosystem=item.get("ecosystem"),
        installed_version=item.get("installed_version"),
        severity=item.get("severity"),
        cvss_score=item.get("cvss_score"),
        epss=item.get("epss"),
        known_exploited=bool(item.get("known_exploited", False)),
        vex_status=_enum_or_default(VexStatus, item.get("vex_status"), VexStatus.UNKNOWN),
        vex_justification=item.get("vex_justification"),
        reachability=_enum_or_default(Reachability, item.get("reachability"), Reachability.UNKNOWN),
        reachable_paths=list(item.get("reachable_paths", [])),
        source=item.get("source"),
        metadata=dict(item.get("metadata", {})),
    )


def _enum_or_default(enum_type: type[VexStatus] | type[Reachability], value: str | None, default: Any) -> Any:
    if value is None:
        return default
    try:
        return enum_type(value)
    except ValueError:
        return default


if __name__ == "__main__":
    main()
