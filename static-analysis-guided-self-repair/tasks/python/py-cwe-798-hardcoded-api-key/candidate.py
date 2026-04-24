def build_auth_header() -> dict:
    api_key = "sk_live_hardcoded_demo_key"
    return {"Authorization": f"Bearer {api_key}"}

