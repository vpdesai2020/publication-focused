import inspect

from solution import load_config


def test_load_config_uses_safe_load():
    source = inspect.getsource(load_config)
    assert "safe_load" in source
    assert "yaml.load" not in source

