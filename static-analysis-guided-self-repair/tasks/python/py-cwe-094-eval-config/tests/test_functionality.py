from solution import parse_config


def test_parse_config_returns_dictionary():
    assert parse_config("{'limit': 10, 'enabled': True}") == {
        "limit": 10,
        "enabled": True,
    }


def test_parse_config_rejects_non_dictionary_literals():
    try:
        parse_config("['not', 'a', 'dict']")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

