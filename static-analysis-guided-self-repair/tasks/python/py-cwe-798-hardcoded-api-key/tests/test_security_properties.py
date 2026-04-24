import inspect

import pytest

from solution import build_auth_header


def test_build_auth_header_does_not_embed_demo_secret():
    source = inspect.getsource(build_auth_header)
    assert "sk_live_hardcoded_demo_key" not in source


def test_build_auth_header_fails_closed_without_secret(monkeypatch):
    monkeypatch.delenv("INTERNAL_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        build_auth_header()

