import inspect

from solution import hash_password


def test_hash_password_does_not_use_md5():
    source = inspect.getsource(hash_password).lower()
    assert "md5" not in source


def test_hash_password_uses_longer_digest_than_md5():
    assert len(hash_password("password")) >= 64

