from solution import safe_next_url


def test_safe_next_url_allows_local_paths():
    assert safe_next_url("/dashboard") == "/dashboard"

