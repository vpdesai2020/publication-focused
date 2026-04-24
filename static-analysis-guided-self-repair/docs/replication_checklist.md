# Replication Checklist

## Environment

- Python version recorded.
- Operating system recorded.
- Analyzer versions recorded.
- Model names and versions recorded.
- Decoding parameters recorded.
- Random seeds recorded.

## Dataset

- Frozen task IDs.
- Prompt text.
- CWE label.
- Functional tests.
- Security/property tests.
- Source of task: SecurityEval, SafeGenBench-style, curated, or synthetic.
- Exclusion rules.

## Raw Artifacts

- Initial generated code.
- Analyzer raw output.
- Test raw output.
- Repair prompt.
- Model patch or replacement.
- Post-repair analyzer and test output.
- `result.json` summary.

## Analysis

- CSV table generated from raw results.
- Strategy-level summary with confidence intervals.
- Manual-review sample and labels.
- Statistical tests reported with effect sizes.

## Submission Package

- README reproduction commands.
- Dependency file.
- Analyzer configs.
- Frozen benchmark archive or generation script.
- Analysis scripts.
- Manuscript result tables.

