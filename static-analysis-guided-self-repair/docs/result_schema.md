# Result Schema

Each experiment run should write one `result.json` per task/model/strategy/seed.

## Required Fields

```json
{
  "task_id": "py-cwe-078-command-injection",
  "model": "fixture",
  "strategy": "multi_analyzer",
  "seed": 1,
  "repair_budget": 3,
  "findings_before": 1,
  "findings_after": 0,
  "findings_removed": 1,
  "findings_introduced": 0,
  "vulnerability_reduction": 1.0,
  "functional_tests_before_ok": true,
  "all_tests_after_ok": true,
  "repair_success": true,
  "manual_review_status": "not_reviewed"
}
```

## Strategy Values

- `none`
- `generic_repair`
- `bandit_feedback`
- `semgrep_feedback`
- `codeql_feedback`
- `multi_analyzer_feedback`
- `fixture`

## Manual Review Values

- `not_reviewed`
- `true_positive_removed`
- `false_positive_removed`
- `true_positive_remaining`
- `regression_or_behavior_loss`
- `unclear`

