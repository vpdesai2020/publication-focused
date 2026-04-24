# Research Plan

## One-Sentence Thesis

Static-analysis findings can be transformed into structured repair feedback that helps LLMs remove security flaws while preserving the functional behavior measured by tests and fuzzing.

## Motivation

LLM-generated code may pass basic tests while still using unsafe APIs, incomplete input validation, weak cryptography, or injection-prone string construction. Existing secure-code benchmarks increasingly measure whether generated code is vulnerable, but a smaller and practical question remains: can a model repair its own generated code using external evidence without breaking behavior?

## Contribution

The intended contribution is intentionally narrow:

1. A repair-loop architecture that explicitly separates functional tests from security/property tests.
2. A structured feedback format for LLM repair prompts that preserves analyzer provenance.
3. An empirical evaluation of vulnerability reduction versus functionality preservation.
4. An ablation study comparing generic repair, single-analyzer repair, and multi-analyzer repair.
5. A manual-review protocol for estimating whether removed findings were real vulnerabilities or analyzer noise.

## Updated Positioning After 2026 Literature Check

The broad idea "use testing and static analysis feedback to help LLMs repair code" is no longer enough by itself. Recent 2026 work already studies detection-to-repair on real developer interactions and feedback-guided code improvement. The defensible version of this project should focus on the measurable tradeoff between **security repair success** and **functionality preservation**, with property/security tests, multi-analyzer disagreement, and false-positive adjudication treated as first-class outcomes.

## Baselines

- **No repair:** first-pass model output.
- **Generic self-reflection:** ask the model to make the code more secure without tool feedback.
- **Single analyzer repair:** Bandit-only for Python, Semgrep-only for cross-language.
- **Multi-analyzer repair:** Bandit + Semgrep + CodeQL where available.

## Experimental Loop

For each benchmark task:

1. Generate `k` candidate solutions from the model.
2. Execute task unit tests and property tests.
3. Run analyzers and normalize findings into a common schema.
4. Build a repair prompt containing only structured evidence and the current code.
5. Apply or record the model patch.
6. Re-run all checks.
7. Stop after success, regression, or a fixed iteration budget.

## Success Criteria

A repair is counted as successful only when:

- The number of confirmed security findings decreases.
- All previously passing unit tests still pass.
- Property-based tests pass within the configured budget.
- The patch does not disable tests, suppress analyzers, remove required behavior, or hard-code test cases.

## Minimum Viable Study

The first publishable prototype can be Python-only:

- 50 to 100 SecurityEval-style tasks.
- 2 to 4 models.
- Bandit + Semgrep, with CodeQL added when install time permits.
- Three repair attempts per generated sample.
- Manual adjudication for a stratified sample of analyzer findings to estimate false positives.
- Separate functional tests from security/property tests so initially vulnerable code can still be counted as functionally valid.

## Stronger Journal Study

The stronger version adds:

- Multiple languages: Python, JavaScript, Java.
- SafeGenBench-style task categories.
- CodeQL for languages with mature query packs.
- Fuzz tests for input-validation-heavy tasks.
- Statistical tests over repair success, regression rate, and analyzer agreement.
