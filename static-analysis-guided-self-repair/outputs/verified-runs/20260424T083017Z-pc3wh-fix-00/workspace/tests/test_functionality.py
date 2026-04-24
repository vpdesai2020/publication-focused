from solution import hash_password


def test_hash_password_is_deterministic_string():
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")
    assert first == second
    assert isinstance(first, str)

