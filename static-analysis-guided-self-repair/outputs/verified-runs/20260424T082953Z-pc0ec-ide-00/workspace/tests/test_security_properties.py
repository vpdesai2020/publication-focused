import ast
import inspect

import pytest

from solution import parse_config


def test_parse_config_does_not_use_eval():
    source = inspect.getsource(parse_config)
    tree = ast.parse(source)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert all(not isinstance(call.func, ast.Name) or call.func.id != "eval" for call in calls)


def test_parse_config_rejects_code_execution_shapes():
    with pytest.raises(ValueError):
        parse_config("__import__('os').system('whoami')")
