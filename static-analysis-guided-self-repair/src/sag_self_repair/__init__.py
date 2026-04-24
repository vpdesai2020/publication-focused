"""Static-analysis-guided self-repair research prototype."""

from .metrics import repair_success, vulnerability_reduction
from .model_provider import CommandProvider, FixtureProvider
from .repair_prompt import build_repair_prompt
from .results import TrialRecord, summarize_trials
from .schema import AnalyzerRun, RepairIteration, TestRun, ToolFinding
from .tasks import TaskSpec, load_task_spec

__all__ = [
    "AnalyzerRun",
    "CommandProvider",
    "FixtureProvider",
    "RepairIteration",
    "TaskSpec",
    "TestRun",
    "ToolFinding",
    "TrialRecord",
    "build_repair_prompt",
    "load_task_spec",
    "repair_success",
    "summarize_trials",
    "vulnerability_reduction",
]
