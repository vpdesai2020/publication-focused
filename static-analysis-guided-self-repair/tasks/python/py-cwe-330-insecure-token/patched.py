import secrets


def make_reset_token(user_id: str) -> str:
    return f"{user_id}-{secrets.token_urlsafe(24)}"

