from pathlib import Path

from sag_self_repair.builtin_analyzer import analyze_python_file
from sag_self_repair.results import TrialRecord, summarize_trials
from sag_self_repair.schema import AnalyzerRun, RepairIteration, TestRun, ToolFinding
from sag_self_repair.stats import sign_test_two_sided, wilson_interval
from sag_self_repair.tasks import load_task_spec


def test_builtin_analyzer_detects_shell_true(tmp_path):
    source = tmp_path / "solution.py"
    source.write_text(
        "import subprocess\n"
        "def run(name):\n"
        "    return subprocess.check_output(name, shell=True)\n",
        encoding="utf-8",
    )
    run = analyze_python_file(source)
    assert run.findings[0].rule_id == "python.subprocess.shell-true"
    assert run.findings[0].cwe == "CWE-078"


def test_task_loader_reads_directory_spec():
    task = load_task_spec(Path("tasks/python/py-cwe-078-command-injection"))
    assert task.id == "py-cwe-078-command-injection"
    assert task.patched_file == "patched.py"


def test_summarize_trials_reports_success_rate():
    finding = ToolFinding(
        tool="builtin-python",
        rule_id="python.subprocess.shell-true",
        message="Avoid shell=True",
        path="solution.py",
        line=5,
        cwe="CWE-078",
    )
    before = RepairIteration(
        task_id="task",
        iteration=0,
        analyzer_runs=(AnalyzerRun("builtin-python", 1, (finding,)),),
        test_runs=(
            TestRun("pytest:functional", 0, kind="functional", passed=2, failed=0),
            TestRun("pytest:security", 1, kind="security", passed=0, failed=1),
        ),
    )
    after = RepairIteration(
        task_id="task",
        iteration=1,
        analyzer_runs=(AnalyzerRun("builtin-python", 0, ()),),
        test_runs=(
            TestRun("pytest:functional", 0, kind="functional", passed=2, failed=0),
            TestRun("pytest:security", 0, kind="security", passed=3, failed=0),
        ),
    )
    summary = summarize_trials([TrialRecord("task", "fixture", before, after)])
    assert summary["trials"] == 1
    assert summary["repair_success_rate"] == 1.0
    assert summary["mean_vulnerability_reduction"] == 1.0


def test_statistical_helpers_are_bounded():
    lower, upper = wilson_interval(5, 10)
    assert 0 <= lower <= upper <= 1
    assert sign_test_two_sided(10, 0) < 0.01
    assert sign_test_two_sided(0, 0) == 1.0
