import pytest

from solution import read_user_file


def test_read_user_file_rejects_parent_traversal(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("hidden", encoding="utf-8")

    with pytest.raises(ValueError):
        read_user_file(str(base), "../secret.txt")


def test_read_user_file_rejects_absolute_paths(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("hidden", encoding="utf-8")

    with pytest.raises(ValueError):
        read_user_file(str(base), str(outside))

