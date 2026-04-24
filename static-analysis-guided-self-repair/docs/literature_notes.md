# Literature Notes

These are starter anchors, not a complete literature review.

## Secure Code Generation Benchmarks

- **SafeGenBench**: Li et al. introduce a benchmark for security vulnerability detection in LLM-generated code and an automatic evaluation framework using SAST and LLM-based judging. arXiv page: https://arxiv.org/abs/2506.05692
- **SecRepoBench**: Shen et al. evaluate code agents on secure code completion in real repositories, with C/C++ tasks and CWE coverage. arXiv page: https://arxiv.org/abs/2504.21205
- **SecurityEval**: Siddiq and Santos provide CWE-mapped samples for evaluating code generation security. ACM DOI: https://doi.org/10.1145/3549035.3561184 and dataset card: https://huggingface.co/datasets/s2e-lab/SecurityEval

## Closest 2026 Work

- **Secure coding with AI - from detection to repair**: Belozerov, Barclay, and Sami study GPT-generated code from DevGPT, use static scanners plus manual inspection, and evaluate GPT-4.1, GPT-5, and Claude Opus 4.1 for vulnerability detection and repair. Published in Empirical Software Engineering on 13 March 2026. https://link.springer.com/article/10.1007/s10664-026-10812-8
- **Helping LLMs improve code generation using feedback from testing and static analysis**: Dolcetti et al. present a framework that uses testing and static analysis feedback to guide self-improvement of open-source LLM-generated C code. Published in Discover Artificial Intelligence on 5 March 2026. https://link.springer.com/article/10.1007/s44163-026-01009-5
- **Why LLMs Fail**: Al-Maamari analyzes LLM-generated security patches across Java vulnerabilities using security and functionality axes, reporting that full correctness remains difficult. arXiv: https://arxiv.org/abs/2603.10072
- **Leveraging Static Analysis for Feedback-Driven Security Patching in LLM-Generated Code**: reports Bandit/CodeQL/Semgrep-style feedback-driven patching for Python. This is very close to the original project idea, so this project needs sharper differentiation around functionality preservation, property tests, cross-analyzer disagreement, and manual false-positive review. https://www.mdpi.com/2624-800X/5/4/110

## Tooling Anchors

- CodeQL CLI documentation: https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line
- Semgrep CLI reference: https://semgrep.dev/docs/cli-reference
- Bandit getting started guide: https://bandit.readthedocs.io/en/latest/start.html
- Hypothesis documentation: https://hypothesis.readthedocs.io/

## Gap Statement

Current benchmark work helps identify whether generated code is vulnerable, and recent feedback-guided repair work already shows that static-analysis feedback can improve repair. The revised gap is narrower: under a fixed repair budget, when does analyzer-guided repair reduce confirmed vulnerability evidence while preserving functional behavior under unit and property/security tests?

## Positioning

This project sits between secure code generation, automated program repair, and empirical software engineering. It should avoid overclaiming "security correctness" from SAST alone. The paper should claim measurable vulnerability reduction under defined analyzer/test oracles, then separately report manual validation and tool disagreement.
