import inspect

from solution import make_reset_token


def test_make_reset_token_uses_secrets_not_random():
    source = inspect.getsource(make_reset_token)
    assert "random." not in source
    assert "secrets." in source


def test_make_reset_token_has_substantial_entropy_material():
    token = make_reset_token("alice")
    suffix = token.split("-", 1)[1]
    assert len(suffix) >= 24

