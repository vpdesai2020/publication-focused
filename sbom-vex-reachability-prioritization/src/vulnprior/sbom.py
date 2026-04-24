from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from .maven import MavenDependency


@dataclass(frozen=True, slots=True)
class SbomComponent:
    name: str
    version: str | None
    package_url: str | None
    ecosystem: str | None
    group: str | None = None
    bom_ref: str | None = None


def load_cyclonedx_components(path: Path) -> list[SbomComponent]:
    """Load package-like components from a CycloneDX JSON SBOM."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    components = []
    for component in payload.get("components", []):
        package_url = component.get("purl")
        package_info = parse_maven_purl(package_url)
        group = component.get("group") or (package_info[0] if package_info else None)
        name = component.get("name", "")
        if package_info and not name:
            name = package_info[1]
        components.append(
            SbomComponent(
                name=name,
                version=component.get("version"),
                package_url=package_url,
                ecosystem=_ecosystem_from_purl(package_url),
                group=group,
                bom_ref=component.get("bom-ref"),
            )
        )
    return components


def load_cyclonedx_maven_dependencies(path: Path) -> list[MavenDependency]:
    """Load Maven package components from a CycloneDX JSON SBOM."""
    dependencies = []
    seen = set()
    for component in load_cyclonedx_components(path):
        if component.ecosystem != "Maven" or not component.version:
            continue
        package_info = parse_maven_purl(component.package_url)
        if package_info:
            group_id, artifact_id, version = package_info
        else:
            group_id = component.group
            artifact_id = component.name
            version = component.version
        if not group_id or not artifact_id or not version:
            continue
        key = (group_id, artifact_id, version)
        if key in seen:
            continue
        seen.add(key)
        dependencies.append(
            MavenDependency(
                group_id=group_id,
                artifact_id=artifact_id,
                version=version,
                scope=None,
                optional=False,
                pom_path=str(path.name),
                parser="syft-cyclonedx",
            )
        )
    return sorted(dependencies, key=lambda item: (item.name, item.version))


def parse_maven_purl(package_url: str | None) -> tuple[str, str, str] | None:
    if not package_url or not package_url.startswith("pkg:maven/"):
        return None
    value = package_url.removeprefix("pkg:maven/").split("?", 1)[0]
    if "@" not in value:
        return None
    name_part, version = value.rsplit("@", 1)
    parts = [unquote(part) for part in name_part.split("/") if part]
    if len(parts) < 2 or not version:
        return None
    group_id = "/".join(parts[:-1])
    artifact_id = parts[-1]
    return group_id, artifact_id, unquote(version)


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
