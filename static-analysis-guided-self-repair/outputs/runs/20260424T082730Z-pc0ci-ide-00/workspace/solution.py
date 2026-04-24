import subprocess


def run_backup(name: str) -> str:
    command = f"echo backing up {name}"
    return subprocess.check_output(command, shell=True, text=True)

