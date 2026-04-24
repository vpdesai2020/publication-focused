from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


PROPERTY_PATTERN = re.compile(r"\$\{([^}]+)\}")


@dataclass(frozen=True, slots=True)
class MavenDependency:
    group_id: str
    artifact_id: str
    version: str
    scope: str | None
    optional: bool
    pom_path: str
    parser: str = "maven-pom"

    @property
    def name(self) -> str:
        return f"{self.group_id}:{self.artifact_id}"

    @property
    def package_url(self) -> str:
        return f"pkg:maven/{self.group_id}/{self.artifact_id}@{self.version}"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "group_id": self.group_id,
            "artifact_id": self.artifact_id,
            "version": self.version,
            "ecosystem": "Maven",
            "package_url": self.package_url,
            "scope": self.scope,
            "optional": self.optional,
            "pom_path": self.pom_path,
            "parser": self.parser,
        }


@dataclass(slots=True)
class MavenContext:
    properties: dict[str, str] = field(default_factory=dict)
    managed_versions: dict[str, str] = field(default_factory=dict)


def collect_maven_dependencies(repo_path: Path, include_test: bool = False) -> list[MavenDependency]:
    pom_paths = [
        path
        for path in repo_path.rglob("pom.xml")
        if not _is_ignored_path(path)
    ]
    dependencies: dict[tuple[str, str, str, str], MavenDependency] = {}
    for pom_path in pom_paths:
        for dependency in _parse_pom_dependencies(repo_path, pom_path, include_test):
            key = (
                dependency.group_id,
                dependency.artifact_id,
                dependency.version,
                dependency.pom_path,
            )
            dependencies[key] = dependency
    return sorted(dependencies.values(), key=lambda item: (item.name, item.version, item.pom_path))


def _parse_pom_dependencies(repo_path: Path, pom_path: Path, include_test: bool) -> list[MavenDependency]:
    try:
        root = ET.parse(pom_path).getroot()
    except ET.ParseError:
        return []

    context = _load_context(pom_path, set())
    dependencies = []
    for dependency in _children(_child(root, "dependencies"), "dependency"):
        group_id = _resolve(_text(_child(dependency, "groupId")), context.properties)
        artifact_id = _resolve(_text(_child(dependency, "artifactId")), context.properties)
        version = _resolve(_text(_child(dependency, "version")), context.properties)
        scope = _resolve(_text(_child(dependency, "scope")), context.properties)
        optional = (_resolve(_text(_child(dependency, "optional")), context.properties) or "").lower() == "true"
        if not group_id or not artifact_id:
            continue
        if not version:
            version = context.managed_versions.get(f"{group_id}:{artifact_id}")
        version = _resolve(version, context.properties)
        if not version or "${" in version:
            continue
        if not include_test and scope == "test":
            continue
        dependencies.append(
            MavenDependency(
                group_id=group_id,
                artifact_id=artifact_id,
                version=version,
                scope=scope,
                optional=optional,
                pom_path=str(pom_path.relative_to(repo_path)),
            )
        )
    return dependencies


def _load_context(pom_path: Path, seen: set[Path]) -> MavenContext:
    pom_path = pom_path.resolve()
    if pom_path in seen:
        return MavenContext()
    seen.add(pom_path)

    try:
        root = ET.parse(pom_path).getroot()
    except ET.ParseError:
        return MavenContext()

    parent_context = MavenContext()
    parent = _child(root, "parent")
    if parent is not None:
        relative_path = _text(_child(parent, "relativePath")) or "../pom.xml"
        parent_path = (pom_path.parent / relative_path).resolve()
        if parent_path.is_dir():
            parent_path = parent_path / "pom.xml"
        if parent_path.exists() and parent_path.name == "pom.xml":
            parent_context = _load_context(parent_path, seen)

    context = MavenContext(
        properties=dict(parent_context.properties),
        managed_versions=dict(parent_context.managed_versions),
    )

    artifact_id = _text(_child(root, "artifactId"))
    group_id = _text(_child(root, "groupId")) or _text(_child(parent, "groupId"))
    version = _text(_child(root, "version")) or _text(_child(parent, "version"))
    if group_id:
        context.properties["project.groupId"] = _resolve(group_id, context.properties) or group_id
        context.properties["pom.groupId"] = context.properties["project.groupId"]
    if artifact_id:
        context.properties["project.artifactId"] = artifact_id
        context.properties["pom.artifactId"] = artifact_id
    if version:
        context.properties["project.version"] = _resolve(version, context.properties) or version
        context.properties["pom.version"] = context.properties["project.version"]

    properties = _child(root, "properties")
    for property_node in list(properties) if properties is not None else []:
        context.properties[_tag(property_node)] = _resolve(_text(property_node), context.properties) or ""

    dependency_management = _child(root, "dependencyManagement")
    managed_dependencies = _child(dependency_management, "dependencies")
    for dependency in _children(managed_dependencies, "dependency"):
        group_id = _resolve(_text(_child(dependency, "groupId")), context.properties)
        artifact_id = _resolve(_text(_child(dependency, "artifactId")), context.properties)
        version = _resolve(_text(_child(dependency, "version")), context.properties)
        if group_id and artifact_id and version:
            context.managed_versions[f"{group_id}:{artifact_id}"] = version

    return context


def _resolve(value: str | None, properties: dict[str, str], depth: int = 0) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if depth > 8:
        return value

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return properties.get(key, match.group(0))

    resolved = PROPERTY_PATTERN.sub(replace, value)
    if resolved != value and "${" in resolved:
        return _resolve(resolved, properties, depth + 1)
    return resolved


def _child(node: ET.Element | None, name: str) -> ET.Element | None:
    if node is None:
        return None
    for child in list(node):
        if _tag(child) == name:
            return child
    return None


def _children(node: ET.Element | None, name: str) -> list[ET.Element]:
    if node is None:
        return []
    return [child for child in list(node) if _tag(child) == name]


def _tag(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def _text(node: ET.Element | None) -> str | None:
    if node is None or node.text is None:
        return None
    return node.text.strip()


def _is_ignored_path(path: Path) -> bool:
    ignored = {".git", "target", "build", "out", ".mvn"}
    return any(part in ignored for part in path.parts)

