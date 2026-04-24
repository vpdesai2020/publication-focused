import yaml


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.load(handle, Loader=yaml.Loader)
    return data or {}

