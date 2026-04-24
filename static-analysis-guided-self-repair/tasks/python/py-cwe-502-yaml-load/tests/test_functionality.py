from solution import load_config


def test_load_config_reads_mapping(tmp_path):
    config = tmp_path / "config.yml"
    config.write_text("name: demo\nlimit: 3\n", encoding="utf-8")
    assert load_config(str(config)) == {"name": "demo", "limit": 3}


def test_load_config_empty_file_returns_empty_dict(tmp_path):
    config = tmp_path / "config.yml"
    config.write_text("", encoding="utf-8")
    assert load_config(str(config)) == {}

