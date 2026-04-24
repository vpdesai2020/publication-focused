def parse_config(text: str) -> dict:
    value = eval(text)
    if not isinstance(value, dict):
        raise ValueError("Config must be a dictionary")
    return value

