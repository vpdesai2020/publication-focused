# Static-Analysis-Guided Self-Repair of LLM-Generated Code with Functionality Preservation

## Abstract

Large language models can generate code that passes basic functional tests while retaining security weaknesses. Prior work has shown that static-analysis feedback can improve generated code, but less is known about the tradeoff between security repair and functionality preservation under explicit repair budgets. We present a repair loop that converts findings from static analyzers, unit tests, and property/security tests into structured feedback for LLM patch generation. The evaluation measures vulnerability-evidence reduction, functional preservation, regression rate, analyzer agreement, and manually reviewed false positives. This manuscript is currently a scaffold; empirical results must be populated from the frozen benchmark runs before submission.

## 1. Introduction

AI-generated code is increasingly used in security-sensitive development workflows. The central risk is not only that generated code can be vulnerable, but that it may appear correct under ordinary tests. This paper studies whether tool-guided repair can reduce vulnerability evidence while preserving intended behavior.

The contribution is intentionally narrow:

- A reproducible repair-loop framework that separates functional tests from security/property tests.
- A structured feedback representation for analyzer and test evidence.
- A benchmark protocol for measuring security repair success under functionality-preservation constraints.
- An evaluation plan covering no repair, generic repair, single-analyzer feedback, and multi-analyzer feedback.

## 2. Background and Related Work

Recent benchmark work, including SafeGenBench and SecurityEval-style datasets, shows that secure code generation remains under-evaluated relative to functional correctness. Feedback-driven repair is now an active area, with recent studies using testing and static-analysis reports to guide LLM refinement. This paper differentiates itself by making functionality preservation and analyzer disagreement primary measured outcomes rather than secondary checks.

## 3. Method

For each task, the pipeline records the prompt, generated code, analyzer findings, functional-test output, security/property-test output, repair prompt, patch, and post-repair outcomes. A repair succeeds only when vulnerability evidence is reduced and all functional and security/property tests pass after repair.

### 3.1 Structured Feedback

The feedback includes analyzer name, rule ID, severity, CWE, file, line, message, and test-output tails. The prompt instructs the model to produce minimal behavior-preserving patches without suppressing analyzers or weakening tests.

### 3.2 Strategies

- No repair.
- Generic repair without analyzer evidence.
- Bandit-guided repair.
- Semgrep-guided repair.
- CodeQL-guided repair.
- Multi-analyzer repair.

## 4. Experimental Design

The minimum study freezes a Python benchmark subset with task IDs, CWE labels, prompts, candidate programs, functional tests, and security/property tests. Each model is sampled under fixed decoding parameters and repaired under a fixed iteration budget.

Primary outcomes:

- Vulnerability reduction.
- Repair success.
- Functionality preservation.
- Regression rate.
- Analyzer agreement.
- Manual true-positive rate.

## 5. Results

Populate after running the frozen experiment:

- Table 1: dataset summary by CWE.
- Table 2: analyzer coverage and agreement.
- Table 3: repair success by strategy and model.
- Table 4: functionality preservation and regression rate.
- Table 5: manual validation labels.

## 6. Discussion

Discuss whether multi-analyzer feedback improves repair success, where it causes regressions, and which CWEs resist repair. Explicitly separate "removed analyzer finding" from "confirmed vulnerability fixed."

## 7. Threats to Validity

Static analyzers are incomplete and can produce false positives. Functional tests and property/security tests are partial behavior oracles. Generated code may be contaminated by benchmark exposure. Model APIs and versions change over time. The study mitigates these risks through frozen artifacts, manual review, open scripts, and explicit tool-version reporting.

## 8. Conclusion

The paper should conclude only after empirical runs are complete. The expected contribution is an evidence-backed measurement of when static-analysis-guided repair makes LLM-generated code safer without breaking behavior.

