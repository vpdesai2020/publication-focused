# SBOM- and VEX-Aware Reachability Analysis for Actionable Open-Source Vulnerability Prioritization

Working folder for a publishable research project on reducing noisy dependency vulnerability alerts by combining accurate SBOM generation, VEX applicability signals, and lightweight reachability analysis.

## Research Aim

Current dependency scanners often rank alerts by package/version matching and CVSS severity. This project tests whether a practical pipeline can produce more actionable alerts by asking three extra questions:

1. Is the dependency inventory accurate enough to trust?
2. Does available VEX data say the product is actually affected?
3. Is vulnerable code reachable from the application?

The intended contribution is a reproducible prioritization method that ranks vulnerabilities by contextual exploitability and code reachability instead of CVSS alone.

## Initial Contributions

- A lockfile-first SBOM workflow using CycloneDX/Syft outputs.
- A VEX-aware normalizer for affected, not affected, fixed, and under investigation statuses.
- A reachability enrichment layer, initially scoped to Java/Kotlin call graphs from CodeQL.
- A transparent scoring model that can be compared against CVSS-only, OSV-only, and scanner-default baselines.
- An empirical evaluation design for public open-source repositories.

## Evidence Base

- O'Donoghue et al., "Software Bill of Materials in Software Supply Chain Security A Systematic Literature Review", arXiv:2506.03507. Note: the arXiv record is currently withdrawn and should be treated as motivation only until a stable version is available.
- Zhou, Dacier, and Konstantinou, "A Reality Check on SBOM-based Vulnerability Management: An Empirical Study and A Path Forward", arXiv:2511.20313. Latest arXiv v2 reports a 92.0% false-positive rate in its case study and 61.9% pruning of false alarms by function-call analysis.
- OpenVEX specification: VEX complements SBOMs by describing whether vulnerability findings apply to a product.
- CycloneDX VEX capability: machine-readable exploitability status for vulnerabilities in a product context.

## Project Layout

```text
.
|-- README.md
|-- pyproject.toml
|-- docs/
|   |-- experiment-plan.md
|   |-- literature-map.md
|   `-- methodology.md
|-- examples/
|   |-- sample_findings.json
|   `-- sample_openvex.json
|-- queries/
|   `-- codeql/
|       `-- java/
|           `-- export-call-edges.ql
|-- src/
|   `-- vulnprior/
|       |-- __init__.py
|       |-- cli.py
|       |-- models.py
|       |-- osv_client.py
|       |-- ranker.py
|       |-- sbom.py
|       `-- vex.py
`-- data/
    `-- README.md
```

## Prototype Quick Start

```powershell
python -m pip install -e .
python -m vulnprior.cli rank examples/sample_findings.json --out examples/sample_ranked.json
```

Pilot data pipeline:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -B -m vulnprior.cli pilot --config data\pilot_repositories.json --workdir artifacts\pilot --out data\pilot-2026-04-24
```

Example external-tool commands for later experiments:

```powershell
syft dir:.\target-project -o cyclonedx-json=artifacts\sbom.cdx.json
codeql database create artifacts\codeql-db --language=java-kotlin --source-root .\target-project
codeql database analyze artifacts\codeql-db queries\codeql\java\export-call-edges.ql --format=csv --output=artifacts\call-edges.csv
```

## Current Scope

The MVP focuses on Java/Kotlin projects because CodeQL gives a mature call-graph layer. SBOM generation and vulnerability lookup remain format-agnostic where possible so later experiments can extend to npm, PyPI, Cargo, and container images.
