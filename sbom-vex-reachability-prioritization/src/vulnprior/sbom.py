from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SbomComponent:
    name: str
    version: str | None
    package_url: str | None
    ecosystem: str | None


def load_cyclonedx_components(path: Path) -> list[SbomComponent]:
    """Load package-like components from a CycloneDX JSON SBOM."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    components = []
    for component in payload.get("components", []):
        package_url = component.get("purl")
        components.append(
            SbomComponent(
                name=component.get("name", ""),
                version=component.get("version"),
                package_url=package_url,
                ecosystem=_ecosystem_from_purl(package_url),
            )
        )
    return components


def _ecosystem_from_purl(package_url: str | None) -> str | None:
    if not package_url or not package_url.startswith("pkg:"):
        return None
    purl_type = package_url[4:].split("/", 1)[0]
    return {
        "maven": "Maven",
        "npm": "npm",
        "pypi": "PyPI",
        "cargo": "crates.io",
        "golang": "Go",
        "gem": "RubyGems",
        "nuget": "NuGet",
    }.get(purl_type, purl_type)

