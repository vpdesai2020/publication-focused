# Experiment Plan

## Study Design

The study compares four vulnerability-prioritization strategies:

1. CVSS-only ranking.
2. SBOM + vulnerability-feed ranking.
3. SBOM + VEX ranking.
4. SBOM + VEX + reachability ranking.

The main claim is that the fourth strategy should reduce noisy alerts while preserving high-priority actionable findings.

## Dataset

Initial target:

- 30 to 50 Java/Kotlin open-source repositories.
- Maven or Gradle build files with reproducible dependency resolution.
- At least one dependency vulnerability from OSV, GHSA, NVD, Grype, or OSV-Scanner.
- Repositories that build or at least index cleanly with CodeQL.

Expansion target:

- Add npm and Python repositories for SBOM accuracy analysis.
- Keep reachability experiments Java/Kotlin first unless a reliable call graph exists for the ecosystem.

## Baselines

- CVSS descending.
- OSV-Scanner or Grype default output.
- Dependency scanner output with only direct/transitive package matching.
- Optional: Dependabot alert severity if GitHub metadata is available.

## Metrics

- Alert reduction: percentage of alerts downgraded or suppressed.
- Precision@k: manually reviewed actionable findings in the top k.
- Recall of known actionable findings: avoid hiding vulnerabilities that should be patched.
- Time overhead: SBOM generation, vulnerability lookup, CodeQL database creation, query time.
- Explanation quality: percentage of ranked findings with a clear rationale.

## Manual Labeling Rubric

Actionable:

- Vulnerable package version is present.
- Product context or call graph suggests vulnerable code may execute.
- VEX says affected or no trustworthy VEX contradicts applicability.
- A feasible patch, upgrade, mitigation, or configuration change exists.

Likely non-actionable:

- VEX says not affected with a specific justification.
- Vulnerable component namespace is not called by application code.
- Vulnerable code path requires an unused feature, protocol, or configuration.
- Vulnerability applies only to a platform/runtime not used by the project.

Uncertain:

- Advisory lacks vulnerable-symbol detail.
- CodeQL cannot build or misses generated code.
- Reflection, dynamic loading, or dependency injection prevents confident reachability.

## Timeline

Week 1:

- Finish prototype normalization and ranking.
- Select 10 pilot repositories.
- Generate first SBOM and vulnerability corpus.

Week 2:

- Add CodeQL call-edge export and reachability mapping.
- Add VEX parser and example synthetic VEX assertions.

Week 3:

- Run pilot study.
- Manually label top findings.
- Tune scoring caps and confidence labels.

Week 4:

- Scale to 30 to 50 repositories.
- Produce tables, plots, and ablation study.

Week 5:

- Draft paper introduction, related work, method, and threats to validity.

## Venue Fit

- Computers & Security: best fit if the paper emphasizes vulnerability management, security impact, and actionable prioritization.
- Journal of Systems and Software: best fit if the paper emphasizes empirical software engineering, developer alert fatigue, and CI integration.

