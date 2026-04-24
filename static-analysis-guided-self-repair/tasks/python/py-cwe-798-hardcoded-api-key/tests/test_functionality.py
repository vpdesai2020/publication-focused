from solution import build_auth_header


def test_build_auth_header_returns_bearer_header(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_KEY", "test-key")
    header = build_auth_header()
    assert set(header) == {"Authorization"}
    assert header["Authorization"].startswith("Bearer ")
    assert len(header["Authorization"]) > len("Bearer ")
