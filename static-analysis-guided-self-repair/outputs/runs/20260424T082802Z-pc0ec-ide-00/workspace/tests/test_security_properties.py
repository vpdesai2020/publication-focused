import inspect

import pytest

from solution import parse_config


def test_parse_config_does_not_use_eval():
    source = inspect.getsource(parse_config)
    assert "eval(" not in source


def test_parse_config_rejects_code_execution_shapes():
    with pytest.raises(ValueError):
        parse_config("__import__('os').system('whoami')")

