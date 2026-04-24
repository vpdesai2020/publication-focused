# Publication Readiness

## Current Status

Not publication ready.

The project has a reproducible scaffold, literature positioning, task schema, analyzer normalization, metrics, and a runnable local fixture experiment. It does not yet have real experimental results, a frozen benchmark, or a manuscript-grade analysis.

## Why It Is Not Ready

- No real LLM generations or repair patches have been collected.
- Bandit, Semgrep, and CodeQL have not been run on a benchmark sample.
- The benchmark subset is not frozen or justified.
- The current runnable task is only a fixture, not an evaluation dataset.
- No manual validation has been performed to estimate false positives.
- No statistical analysis or confidence intervals have been produced.
- The manuscript has no results section populated with empirical findings.
- Recent 2026 work overlaps with the broad version of the idea, so the novelty must be narrower and cleaner.

## Publication-Ready Definition

This project becomes submission-ready only when it has:

- A frozen dataset of tasks with IDs, CWEs, prompts, functional tests, and security/property tests.
- At least two model families and one open-source model for reproducibility.
- A fixed generation and repair protocol with seeds, decoding parameters, and repair budget.
- External analyzer outputs from Bandit, Semgrep, and CodeQL where supported.
- Ablations for no repair, generic repair, single-analyzer feedback, and multi-analyzer feedback.
- Manual review of a stratified sample of findings.
- Result tables for vulnerability reduction, repair success, functionality preservation, regression rate, and false positives.
- A replication package with scripts, configs, raw outputs, and analysis notebooks or scripts.

## Revised Novelty Claim

The safest novelty claim is:

> We measure when static-analysis-guided LLM repair removes vulnerability evidence without sacrificing functional behavior, using separated functional and property/security tests, multi-analyzer feedback, and manual validation of analyzer disagreement.

Avoid claiming that static-analysis-guided repair itself is new.

## Next Work Packages

1. Freeze a 50-task Python subset from SecurityEval-style prompts.
2. Add or generate functional and security/property tests per task.
3. Run first-pass generation for 2 to 4 models.
4. Run Bandit, Semgrep, and CodeQL on generated code.
5. Run repair conditions under a three-iteration budget.
6. Aggregate results and manually validate a sample.
7. Draft the results, threats, and related-work sections.

