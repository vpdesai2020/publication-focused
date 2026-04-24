import re
import subprocess


_SAFE_BACKUP_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,63}$")


def run_backup(name: str) -> str:
    if not _SAFE_BACKUP_NAME.fullmatch(name) or ".." in name or "/" in name or "\\" in name:
        raise ValueError("Invalid backup name")
    return subprocess.check_output(["echo", "backing up", name], text=True)

