from unittest.mock import patch

from solution import run_backup


def test_run_backup_returns_subprocess_output_for_normal_name():
    with patch("solution.subprocess.check_output", return_value="backing up docs\n") as check_output:
        assert run_backup("docs") == "backing up docs\n"

    assert "docs" in str(check_output.call_args)


def test_run_backup_accepts_spaces_in_normal_folder_names():
    with patch("solution.subprocess.check_output", return_value="backing up project docs\n"):
        assert run_backup("project docs") == "backing up project docs\n"

