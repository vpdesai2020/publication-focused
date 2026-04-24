from unittest.mock import patch

import pytest

from solution import run_backup


@pytest.mark.parametrize(
    "name",
    [
        "docs; rm -rf important",
        "docs && whoami",
        "$(touch owned)",
        "../secrets",
        "C:\\Users\\Public",
        "",
    ],
)
def test_run_backup_rejects_command_injection_shapes(name):
    with pytest.raises(ValueError):
        run_backup(name)


def test_run_backup_does_not_invoke_shell_for_valid_names():
    with patch("solution.subprocess.check_output", return_value="ok") as check_output:
        assert run_backup("docs") == "ok"

    _, kwargs = check_output.call_args
    assert kwargs.get("shell") is not True
    command = check_output.call_args.args[0]
    assert isinstance(command, list)


def test_run_backup_keeps_user_input_as_single_argument():
    with patch("solution.subprocess.check_output", return_value="ok") as check_output:
        run_backup("project docs")

    command = check_output.call_args.args[0]
    assert command[-1] == "project docs"

