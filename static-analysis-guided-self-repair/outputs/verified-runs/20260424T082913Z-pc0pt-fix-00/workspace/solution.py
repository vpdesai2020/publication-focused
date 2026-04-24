from pathlib import Path


def read_user_file(base_dir: str, filename: str) -> str:
    base_path = Path(base_dir).resolve()
    requested_path = (base_path / filename).resolve()
    try:
        requested_path.relative_to(base_path)
    except ValueError as exc:
        raise ValueError("File must stay inside base_dir") from exc
    if requested_path.is_dir():
        raise ValueError("Expected a file")
    return requested_path.read_text(encoding="utf-8")

