from sag_self_repair.analyzers import parse_bandit_json, parse_semgrep_json
from sag_self_repair.metrics import finding_delta, repair_success, vulnerability_reduction
from sag_self_repair.repair_prompt import build_repair_prompt
from sag_self_repair.schema import AnalyzerRun, RepairIteration, TestRun, ToolFinding


def test_vulnerability_reduction_handles_zero_initial_findings():
    assert vulnerability_reduction(0, 0) == 0
    assert vulnerability_reduction(4, 1) == 0.75


def test_repair_success_requires_reduction_and_preserved_tests():
    finding = ToolFinding(
        tool="bandit",
        rule_id="B602",
        message="subprocess call with shell=True",
        path="solution.py",
        line=10,
        severity="high",
        cwe="CWE-078",
    )
    before = RepairIteration(
        task_id="task",
        iteration=0,
        analyzer_runs=(AnalyzerRun("bandit", 1, (finding,)),),
        test_runs=(TestRun("pytest", 0, passed=3, failed=0),),
    )
    after = RepairIteration(
        task_id="task",
        iteration=1,
        analyzer_runs=(AnalyzerRun("bandit", 0, ()),),
        test_runs=(TestRun("pytest", 0, passed=3, failed=0),),
    )
    assert finding_delta(before, after) == {
        "before": 1,
        "after": 0,
        "removed": 1,
        "introduced": 0,
    }
    assert repair_success(before, after)


def test_repair_prompt_contains_structured_feedback_and_constraints():
    iteration = RepairIteration(
        task_id="task",
        iteration=0,
        analyzer_runs=(
            AnalyzerRun(
                "semgrep",
                1,
                (
                    ToolFinding(
                        tool="semgrep",
                        rule_id="python.yaml.unsafe-load",
                        message="Use yaml.safe_load",
                        path="solution.py",
                        line=4,
                        cwe="CWE-502",
                    ),
                ),
            ),
        ),
        test_runs=(TestRun("pytest", 0, passed=1, failed=0, output="1 passed"),),
    )
    prompt = build_repair_prompt("yaml.load(text)", iteration)
    assert "STRUCTURED_FEEDBACK" in prompt
    assert "python.yaml.unsafe-load" in prompt
    assert "minimal patch" in prompt
    assert "yaml.load(text)" in prompt


def test_analyzer_parsers_normalize_cwe_and_location():
    bandit_payload = """
    {
      "results": [
        {
          "test_id": "B602",
          "issue_text": "subprocess call with shell=True",
          "filename": "solution.py",
          "line_number": 8,
          "issue_severity": "HIGH",
          "issue_cwe": {"id": 78}
        }
      ]
    }
    """
    semgrep_payload = """
    {
      "results": [
        {
          "check_id": "python.yaml.unsafe-load",
          "path": "solution.py",
          "start": {"line": 3},
          "extra": {
            "message": "Use yaml.safe_load",
            "severity": "ERROR",
            "metadata": {"cwe": "CWE-502"}
          }
        }
      ]
    }
    """
    bandit_finding = parse_bandit_json(bandit_payload)[0]
    semgrep_finding = parse_semgrep_json(semgrep_payload)[0]
    assert bandit_finding.cwe == "CWE-78"
    assert bandit_finding.line == 8
    assert semgrep_finding.cwe == "CWE-502"
    assert semgrep_finding.rule_id == "python.yaml.unsafe-load"
