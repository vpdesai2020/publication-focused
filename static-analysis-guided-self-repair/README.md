# Static-Analysis-Guided Self-Repair of LLM-Generated Code

Working title: **Static-Analysis-Guided Self-Repair of LLM-Generated Code with Functionality Preservation**.

This project studies whether an iterative repair loop can reduce vulnerabilities in LLM-generated code while preserving functional behavior. The core loop is:

1. Generate candidate code from benchmark prompts.
2. Run static analyzers, unit tests, and fuzz/property tests.
3. Convert failures and findings into structured feedback.
4. Ask the model for a minimal patch.
5. Re-run checks until the code is secure enough, functionality-preserving, or out of budget.

## Research Claim

Recent secure-code benchmarks show that LLM-generated code can be functionally plausible while still containing exploitable patterns. This project targets a narrow, measurable gap: **repair**, not just evaluation. The publishable question is whether multi-analyzer feedback plus functionality checks improves security without breaking expected behavior.

## Primary Research Questions

- **RQ1:** How much does static-analysis-guided self-repair reduce security findings in LLM-generated code?
- **RQ2:** How often do repairs preserve functionality as measured by unit tests and property-based fuzz tests?
- **RQ3:** Does combining CodeQL, Semgrep, and Bandit improve repair quality compared with using a single analyzer?
- **RQ4:** Which vulnerability classes and languages are hardest to repair without regression?

## Suggested Scope

Start with Python only, then extend to JavaScript or Java once the pipeline is stable.

Initial dataset options:

- SecurityEval-style Python tasks for quick iteration.
- SafeGenBench-style prompt/task schema for broader reporting.
- A small curated subset of CWE categories: injection, unsafe deserialization, path traversal, command injection, weak crypto, and SSRF.

## Repository Layout

```text
configs/                  Analyzer configuration.
docs/                     Research plan, literature notes, paper outline.
paper/                    Manuscript draft and paper-facing tables.
scripts/                  CLI entry points for experiments.
src/sag_self_repair/      Repair-loop package.
tasks/                    Starter task schema and examples.
tests/                    Unit tests for project plumbing.
```

## Quick Start

Create a virtual environment, then install local test dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run the smoke demo:

```powershell
python scripts/smoke_demo.py
```

Run the local fixture experiment:

```powershell
python scripts/run_fixture_experiment.py
python scripts/run_task_pack.py --strategy both
python scripts/aggregate_results.py --results-dir outputs
python scripts/summarize_tasks.py
```

Run a command-backed model repair experiment:

```powershell
python scripts/run_command_model_experiment.py --task-dir tasks/python/py-cwe-078-command-injection --model mock --model-command python scripts/mock_repair_model.py
```

Run tests:

```powershell
python -m pytest
```

Static analyzers are optional at first. Install them when you are ready for real experiments:

```powershell
python -m pip install bandit semgrep
```

CodeQL is distributed separately by GitHub and should be installed as a CLI tool.

The fixture experiment uses a small built-in Python analyzer only to validate the experiment pipeline on machines without Bandit, Semgrep, or CodeQL. Do not report built-in analyzer results as the main study.

## Outputs to Track

- Raw generated code and repaired code.
- Analyzer outputs as JSON or SARIF.
- Unit-test and fuzz-test pass/fail results.
- Minimal patch text.
- Iteration count and repair budget.
- Vulnerability reduction and functionality preservation metrics.

## Publication Status

This is not publication ready yet. It is now a reproducible prototype scaffold with a runnable fixture task. To reach paper readiness, the project still needs real model generations, external analyzer runs, a frozen benchmark subset, statistical analysis, manual validation of a sample of findings, and a manuscript with results.

## Target Venues

- Computers & Security
- Journal of Systems and Software
- Empirical Software Engineering
