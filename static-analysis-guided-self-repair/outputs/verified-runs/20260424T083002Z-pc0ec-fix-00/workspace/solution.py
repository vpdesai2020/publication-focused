import ast


def parse_config(text: str) -> dict:
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError) as exc:
        raise ValueError("Invalid config literal") from exc
    if not isinstance(value, dict):
        raise ValueError("Config must be a dictionary")
    return value

