# Paper Outline

## Working Title

Static-Analysis-Guided Self-Repair of LLM-Generated Code with Functionality Preservation

## Abstract Shape

1. Problem: LLM-generated code can pass tests but remain insecure.
2. Gap: existing benchmarks emphasize detection/evaluation more than functionality-preserving repair.
3. Method: iterative repair loop using static analyzers, unit tests, and fuzzing.
4. Results: vulnerability reduction, repair success, regression rate, and analyzer ablation.
5. Implication: external tool feedback can make generated code safer, but repair remains uneven by CWE/language.

## Sections

1. Introduction
2. Background and Related Work
3. Benchmark and Task Construction
4. Static-Analysis-Guided Repair Framework
5. Experimental Setup
6. Results
7. Discussion
8. Threats to Validity
9. Conclusion

## Core Figures

- Repair-loop architecture diagram.
- Vulnerability reduction by analyzer condition.
- Repair success versus regression rate.
- Heatmap by CWE and language.
- Analyzer agreement matrix.

## Core Tables

- Dataset/task summary.
- Models and generation settings.
- Analyzer configuration.
- Main results by condition.
- Ablation results.
- Manual validation confusion table.

## Likely Reviewer Questions

- Are analyzer findings real vulnerabilities or false positives?
- Does the repair only silence tools?
- Are tests strong enough to claim functionality preservation?
- How does this differ from generic self-debugging or APR?
- Does the method work beyond Python?

## Planned Answer to Novelty Concern

The novelty is not a new analyzer or a new LLM. It is an empirical repair framework that measures the tradeoff between vulnerability reduction and behavior preservation, with analyzer ablations and language/CWE breakdowns. This makes the contribution concrete and testable.

