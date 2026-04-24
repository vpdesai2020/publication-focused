# Analyzer Status

## Local Windows Status

As of the current local setup:

- Bandit is installed and produces findings on the Python task pack.
- Semgrep installs, but native Windows execution is not reliable in this environment.
- CodeQL is not installed.

Semgrep 1.161.0 failed during startup with a Windows certificate-store error. Semgrep 1.50.0 and 1.79.0 installed but could not run reliably through the packaged Windows launcher. The scripts now record this as analyzer unavailability rather than treating missing output as "no findings."

## Paper Protocol

The submission-grade experiment should be run in a Linux, WSL, or CI environment where:

- Bandit runs with a pinned version.
- Semgrep runs with `--metrics=off` and `--disable-version-check`.
- CodeQL CLI is installed and its version is recorded.

Local Windows fixture and Bandit runs are useful for pipeline development, but should not be the final reported multi-analyzer evidence.

