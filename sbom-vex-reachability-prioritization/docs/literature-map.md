# Literature Map

## Core Sources

| Source | Why it matters | Notes for the manuscript |
| --- | --- | --- |
| O'Donoghue, Hastings, Ortiz, and Muneza, "Software Bill of Materials in Software Supply Chain Security A Systematic Literature Review", arXiv:2506.03507 | Frames SBOM adoption barriers: generation tooling, analysis tooling, vulnerability exploitability, false positives, maintenance, and trustworthiness. | The current arXiv record is withdrawn for author-approval reasons. Use cautiously and verify a stable version before citation. Link: https://arxiv.org/abs/2506.03507 |
| Zhou, Dacier, and Konstantinou, "A Reality Check on SBOM-based Vulnerability Management: An Empirical Study and A Path Forward", arXiv:2511.20313 | Directly supports the problem statement: accurate lockfile-based SBOMs still lead to noisy downstream vulnerability findings; call analysis prunes many false alarms. | Latest arXiv v2, revised 2026-04-17, reports 92.0% false positives and 61.9% false-alarm pruning. Link: https://arxiv.org/abs/2511.20313 |
| OpenVEX Specification | Defines a minimal VEX format that can be consumed independently of SBOM format. | Useful for arguing interoperability and practical adoption. Link: https://github.com/openvex/spec |
| CycloneDX VEX capability | Establishes VEX as a machine-readable way to communicate whether a vulnerability can actually be exploited in product context. | Useful if the paper emits CycloneDX VEX/BOV artifacts. Link: https://cyclonedx.org/capabilities/vex/ |
| Syft | Mature SBOM generator that supports filesystems, containers, many package ecosystems, CycloneDX, SPDX, and Syft JSON. | Good default SBOM generator for the experimental pipeline. Link: https://github.com/anchore/syft |
| OSV.dev API | Open vulnerability database with package/version and batch-query APIs. | Good public vulnerability feed for reproducibility. Link: https://google.github.io/osv.dev/api/ |
| CodeQL Java/Kotlin call graph documentation | Provides Java/Kotlin call graph abstractions through `Callable` and `Call`. | Good static-analysis backbone for lightweight reachability. Link: https://codeql.github.com/docs/codeql-language-guides/navigating-the-call-graph/ |

## Positioning

This project sits between SBOM quality research, vulnerability-management triage, and static-analysis-assisted reachability. The publishable niche is not "yet another scanner"; it is the integration and evaluation of three practical signals:

1. Accurate dependency inventory from lockfile-aware SBOM generation.
2. Applicability claims from VEX.
3. Application-context reachability from static call graphs.

## Citation Watchlist

- Re-check the withdrawn SLR before submission.
- Re-check the empirical SBOM paper because the public abstract numbers changed between early summaries and arXiv v2.
- Look for related work on Dependabot alert dismissal, Grype/OSV false positives, function-level vulnerability databases, and reachability-based dependency scanning.

