from unittest.mock import Mock, patch

from solution import fetch_profile


def test_fetch_profile_returns_response_text():
    response = Mock(text="profile")
    response.raise_for_status.return_value = None
    with patch("solution.requests.get", return_value=response):
        assert fetch_profile("https://profiles.example.com/alice") == "profile"

