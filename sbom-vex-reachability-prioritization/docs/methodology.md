# Methodology

## Research Questions

RQ1. How much does SBOM + VEX + reachability prioritization reduce non-actionable open-source vulnerability alerts compared with CVSS-only ranking?

RQ2. Which enrichment layer contributes most to actionable prioritization: lockfile-accurate SBOMs, VEX applicability, or call-graph reachability?

RQ3. What is the engineering cost of the enriched pipeline in CI time, required configuration, and manual review effort?

## Pipeline

1. Select public target repositories with reproducible dependency resolution.
2. Generate SBOMs from lockfiles or lockfile-equivalent resolved dependencies.
3. Normalize SBOM components into package URLs where possible.
4. Query public vulnerability feeds such as OSV for package/version findings.
5. Ingest VEX statements from OpenVEX or CycloneDX VEX documents.
6. Build a CodeQL database for Java/Kotlin target projects.
7. Export call graph edges and map application entrypoints to dependency methods.
8. Mark vulnerable components or vulnerable symbols as reachable, unreachable, maybe reachable, or unknown.
9. Rank findings using contextual score rather than CVSS alone.
10. Compare ranked alerts against scanner-default and CVSS-only baselines.

## Data Model

Each normalized vulnerability finding should include:

- Vulnerability ID, aliases, source, and advisory URL.
- Package identifier, ecosystem, version, and package URL.
- Severity features: CVSS, severity label, EPSS if available, known exploited flag if available.
- VEX features: status, justification, author, timestamp, and product match confidence.
- Reachability features: reachable state, path count, entrypoint type, and analysis confidence.
- Ranking outputs: priority score, priority label, and human-readable rationale.

## Reachability Strategy

The first implementation uses Java/Kotlin because CodeQL provides mature call graph primitives. The planned analysis is intentionally lightweight:

- Extract caller-to-callee edges using CodeQL.
- Identify application entrypoints: main methods, web controllers, scheduled jobs, tests excluded by default.
- Map dependency methods to Maven package coordinates through class/package names.
- If advisory metadata has vulnerable symbols, match those symbols directly.
- If advisory metadata lacks symbols, fall back to component-level reachability and mark as maybe reachable when any dependency namespace is called.

This conservative model avoids claiming "safe" when symbol-level evidence is unavailable.

## VEX Strategy

VEX is treated as an applicability signal, not an absolute truth. The ranker should:

- Strongly downgrade `not_affected` when the justification is specific and recent.
- Downgrade `fixed` when the observed version is consistent with the VEX statement.
- Keep `affected` near full weight.
- Treat `under_investigation` as uncertain, not safe.
- Preserve original VEX metadata so reviewers can inspect the assertion.

## Scoring Model

The starting score is transparent and adjustable:

```text
score = severity_weight * severity
      + exploit_weight * exploit_signal
      + reachability_weight * reachability
      + vex_weight * vex_applicability
```

The MVP then applies caps:

- `not_affected` VEX caps the score unless reachability says reachable with high confidence.
- `unreachable` caps the score unless known exploitation is observed.
- Missing reachability remains uncertain rather than low priority.

The final paper should report both ranking quality and alert-volume reduction at fixed review budgets such as top 10, top 25, and top 50 alerts.

## Threats to Validity

- Public repositories may not represent private enterprise build systems.
- Java/Kotlin reachability results may not generalize to dynamic languages.
- Advisory databases often lack vulnerable-symbol metadata.
- VEX statements may be stale, missing, or overly broad.
- Static call graphs may over-approximate or under-approximate runtime behavior, especially with reflection and dependency injection.

