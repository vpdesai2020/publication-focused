# Pilot Data Pipeline

This pilot pipeline creates an initial empirical dataset without requiring Syft, Maven, or CodeQL to be installed locally. It is intentionally conservative and replaceable:

1. Clone a small set of Java/Maven repositories.
2. Generate a Syft CycloneDX SBOM when Syft is available, or parse `pom.xml` files as a fallback.
3. Query OSV for package/version vulnerability findings.
4. Estimate dependency reachability by scanning production Java/Kotlin source files for dependency namespace references.
5. Rank findings with the existing SBOM/VEX/reachability scoring model.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -B -m vulnprior.cli pilot --config data\pilot_repositories.json --workdir artifacts\pilot --out data\pilot-2026-04-24
```

Require Syft/CycloneDX instead of falling back:

```powershell
python -B -m vulnprior.cli pilot --config data\pilot_repositories.json --workdir artifacts\pilot --out data\pilot-syft --sbom-backend syft
```

Outputs:

- `data/pilot-2026-04-24/pilot_summary.md`
- `data/pilot-2026-04-24/pilot_summary.json`
- `data/pilot-2026-04-24/pilot_findings.json`
- `data/pilot-2026-04-24/pilot_ranked.json`
- `data/pilot-2026-04-24/manual-labels-template.csv`
- Per-repository `sbom.cdx.json` and `sbom-info.json` when Syft is used
- Per-repository `components.json`, `findings.json`, and `ranked.json`

Limitations:

- In `auto` mode, Syft is preferred. If Syft is unavailable, the Maven parser is used and the fallback reason is recorded in `sbom-info.json`.
- The Maven parser fallback is not a full dependency resolver and does not yet expand transitive dependencies.
- The reachability check is namespace-level source-reference analysis, not a CodeQL call graph.
- VEX ingestion is available in the prototype, but the pilot run does not assume upstream VEX documents exist for these repositories.

These limits are useful for the paper: they define the baseline pilot before replacing the reachability heuristic with CodeQL.
