# Experiment Design

## Independent Variables

- Model family and size.
- Prompting strategy: direct, security-aware, tool-guided repair.
- Analyzer setup: none, Bandit, Semgrep, CodeQL, combined.
- Repair budget: 0, 1, 2, or 3 iterations.
- Language and CWE category.

## Dependent Variables

- Vulnerability count before and after repair.
- Vulnerability reduction rate.
- Test pass rate before and after repair.
- Property-test pass rate.
- Repair success rate.
- Regression rate.
- False-positive rate after manual review.
- Time and token cost per successful repair.

## Metrics

### Vulnerability Reduction

```text
reduction = (initial_findings - final_findings) / max(initial_findings, 1)
```

Report overall reduction and reduction by analyzer, CWE, severity, model, and language.

### Functionality Preservation

```text
preserved = initial_tests_passed and final_tests_passed and final_fuzz_passed
```

If initial code fails functional tests, report repair separately as "security repair on non-functional code" rather than counting it as functionality-preserving repair.

### Repair Success

```text
success = vulnerability_reduced and functionality_preserved and no_policy_violation
```

### Analyzer Agreement

Track overlap by normalized CWE, path, line range, and message fingerprint. Report cases where one analyzer finds issues missed by another.

## Ablations

1. No feedback versus structured static-analysis feedback.
2. Single analyzer versus combined analyzer feedback.
3. Static-analysis only versus static-analysis plus tests.
4. Free-form prompt versus structured JSON feedback prompt.
5. Full rewrite versus minimal patch instruction.

## Statistical Analysis

- Use paired tests where each prompt/model sample is repaired under multiple conditions.
- Report confidence intervals for reduction and success rates.
- Use logistic regression or mixed-effects models for repair success, with random effects for task when the dataset is large enough.
- Include effect sizes, not only p-values.

## Manual Validation

Static analyzers can over-report. Manually inspect a stratified sample:

- High, medium, and low severity findings.
- Findings removed by repair.
- Findings introduced by repair.
- Disagreements between tools.

The manual validation set should be frozen before final analysis.

