from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Report remaining blockers for publication readiness.")
    parser.add_argument("--tasks-root", type=Path, default=Path("tasks/python"))
    parser.add_argument("--environment", type=Path, default=Path("outputs/analysis/environment.json"))
    parser.add_argument("--manual-review", type=Path, default=Path("outputs/analysis/manual_review_sheet.csv"))
    parser.add_argument("--minimum-tasks", type=int, default=50)
    args = parser.parse_args()

    task_count = len(list(args.tasks_root.rglob("task.json")))
    environment = _load_json(args.environment)
    tools = environment.get("tools", {}) if environment else {}
    packages = environment.get("packages", {}) if environment else {}
    manual_review = _manual_review_status(args.manual_review)

    checks = {
        "minimum_task_count": {
            "ok": task_count >= args.minimum_tasks,
            "current": task_count,
            "required": args.minimum_tasks,
        },
        "bandit_available": {
            "ok": _tool_available(tools, packages, "bandit"),
            "details": tools.get("bandit") or packages.get("bandit"),
        },
        "semgrep_available": {
            "ok": _tool_available(tools, packages, "semgrep") and bool(tools.get("semgrep", {}).get("available")),
            "details": tools.get("semgrep") or packages.get("semgrep"),
        },
        "codeql_available": {
            "ok": bool(tools.get("codeql", {}).get("available")),
            "details": tools.get("codeql"),
        },
        "manual_review_started": manual_review,
    }
    blockers = [name for name, check in checks.items() if not check["ok"]]
    payload = {
        "publication_ready": not blockers,
        "blockers": blockers,
        "checks": checks,
    }
    print(json.dumps(payload, indent=2))


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _tool_available(tools: dict, packages: dict, name: str) -> bool:
    return bool(tools.get(name, {}).get("available") or packages.get(name, {}).get("available"))


def _manual_review_status(path: Path) -> dict:
    if not path.exists():
        return {"ok": False, "reviewed_rows": 0, "total_rows": 0}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    reviewed = [row for row in rows if row.get("review_label")]
    return {
        "ok": bool(reviewed),
        "reviewed_rows": len(reviewed),
        "total_rows": len(rows),
    }


if __name__ == "__main__":
    main()

