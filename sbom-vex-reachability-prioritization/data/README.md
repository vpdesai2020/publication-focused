# Data Folder

Use this folder for experiment metadata and derived datasets only.

Recommended structure:

```text
data/
|-- repositories.csv
|-- findings-normalized.jsonl
|-- manual-labels.csv
`-- runs/
```

Avoid storing full cloned repositories, large CodeQL databases, or generated build artifacts here. Store those under `artifacts/` or outside the paper folder and document how to reproduce them.

Current pilot output:

- `pilot_repositories.json`: three-repository Java/Maven pilot configuration.
- `pilot-2026-04-24/`: first successful OSV-backed pilot run.
