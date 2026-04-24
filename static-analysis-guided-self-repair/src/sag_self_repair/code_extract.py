from __future__ import annotations

import re


_FENCED_BLOCK = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)


def extract_python_code(text: str) -> str:
    match = _FENCED_BLOCK.search(text)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"

