from urllib.parse import urlparse

import requests


_ALLOWED_HOSTS = {"profiles.example.com"}


def fetch_profile(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_HOSTS:
        raise ValueError("URL host is not allowed")
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.text

