from pathlib import Path


def read_user_file(base_dir: str, filename: str) -> str:
    path = Path(base_dir) / filename
    return path.read_text(encoding="utf-8")

