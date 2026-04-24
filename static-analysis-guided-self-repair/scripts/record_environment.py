from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Record environment and analyzer versions.")
    parser.add_argument("--output", type=Path, default=Path("outputs/analysis/environment.json"))
    args = parser.parse_args()

    payload = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "tools": {
            "bandit": _version(["bandit", "--version"]),
            "semgrep": _version(["semgrep", "--version"]),
            "codeql": _version(["codeql", "version"]),
        },
        "packages": {
            "bandit": _pip_show("bandit"),
            "semgrep": _pip_show("semgrep"),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


def _version(command: list[str]) -> dict:
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": completed.returncode == 0 and bool(completed.stdout.strip() or completed.stderr.strip()),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "empty_output": not bool(completed.stdout.strip() or completed.stderr.strip()),
    }


def _pip_show(package: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "show", package],
        text=True,
        capture_output=True,
        check=False,
    )
    fields = {}
    for line in completed.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()
    return {
        "available": completed.returncode == 0,
        "version": fields.get("version"),
        "location": fields.get("location"),
    }


if __name__ == "__main__":
    main()
