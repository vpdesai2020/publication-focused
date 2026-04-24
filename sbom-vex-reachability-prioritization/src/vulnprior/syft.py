from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .maven import MavenDependency
from .sbom import load_cyclonedx_maven_dependencies


class SyftUnavailable(RuntimeError):
    """Raised when the Syft executable cannot be found."""


@dataclass(frozen=True, slots=True)
class SyftSbomResult:
    sbom_path: Path
    components: list[MavenDependency]
    command: list[str]
    version: str | None


def syft_available(syft_bin: str = "syft") -> bool:
    return shutil.which(syft_bin) is not None or Path(syft_bin).exists()


def generate_syft_cyclonedx_maven_components(
    repo_path: Path,
    sbom_path: Path,
    syft_bin: str = "syft",
) -> SyftSbomResult:
    if not syft_available(syft_bin):
        raise SyftUnavailable(f"Syft executable not found: {syft_bin}")

    sbom_path.parent.mkdir(parents=True, exist_ok=True)
    command = [syft_bin, "dir:.", "-o", f"cyclonedx-json={sbom_path.resolve()}"]
    result = subprocess.run(command, cwd=repo_path, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"Syft CycloneDX generation failed: {detail}")
    if not sbom_path.exists():
        raise RuntimeError(f"Syft completed but did not create {sbom_path}")

    return SyftSbomResult(
        sbom_path=sbom_path,
        components=load_cyclonedx_maven_dependencies(sbom_path),
        command=command,
        version=syft_version(syft_bin),
    )


def syft_version(syft_bin: str = "syft") -> str | None:
    if not syft_available(syft_bin):
        return None
    result = subprocess.run([syft_bin, "version"], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else None

