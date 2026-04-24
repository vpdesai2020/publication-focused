from solution import safe_next_url


def test_safe_next_url_blocks_external_absolute_urls():
    assert safe_next_url("https://evil.example/login") == "/"


def test_safe_next_url_blocks_scheme_relative_urls():
    assert safe_next_url("//evil.example/login") == "/"


def test_safe_next_url_blocks_relative_without_leading_slash():
    assert safe_next_url("evil") == "/"

