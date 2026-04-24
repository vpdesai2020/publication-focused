from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> None:
    prompt = sys.stdin.read()
    task_id = _task_id(prompt)
    if not task_id:
        raise SystemExit("Could not find task_id in prompt")
    patched = Path("tasks/python") / task_id / "patched.py"
    if not patched.exists():
        raise SystemExit(f"Missing patched fixture for {task_id}")
    code = patched.read_text(encoding="utf-8")
    print("```python")
    print(code.rstrip())
    print("```")


def _task_id(prompt: str) -> str | None:
    match = re.search(r"STRUCTURED_FEEDBACK:\s*(\{.*?\})\s*CURRENT_CODE:", prompt, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1)).get("task_id")
    except json.JSONDecodeError:
        return None


if __name__ == "__main__":
    main()

