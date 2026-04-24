from unittest.mock import patch

import pytest

from solution import fetch_profile


@pytest.mark.parametrize(
    "url",
    [
        "http://profiles.example.com/alice",
        "https://127.0.0.1/admin",
        "https://169.254.169.254/latest/meta-data",
        "https://evil.example.com/alice",
    ],
)
def test_fetch_profile_rejects_untrusted_urls(url):
    with patch("solution.requests.get") as get:
        with pytest.raises(ValueError):
            fetch_profile(url)
    get.assert_not_called()

