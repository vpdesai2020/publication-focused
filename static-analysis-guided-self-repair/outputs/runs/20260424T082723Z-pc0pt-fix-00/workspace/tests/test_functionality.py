from solution import read_user_file


def test_read_user_file_reads_file_inside_base_dir(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    (base / "note.txt").write_text("hello", encoding="utf-8")
    assert read_user_file(str(base), "note.txt") == "hello"

