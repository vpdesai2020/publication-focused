from solution import make_reset_token


def test_make_reset_token_contains_user_id_prefix():
    token = make_reset_token("alice")
    assert token.startswith("alice-")
    assert len(token) > len("alice-")

