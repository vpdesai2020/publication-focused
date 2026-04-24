import os


def build_auth_header() -> dict:
    api_key = os.environ.get("INTERNAL_API_KEY")
    if not api_key:
        raise RuntimeError("INTERNAL_API_KEY is not configured")
    return {"Authorization": f"Bearer {api_key}"}

