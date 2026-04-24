# Pilot Results: 2026-04-24

## Run Command

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Resolve-Path .\src).Path
$pilotWork = Join-Path $env:TEMP 'vulnprior-pilot'
python -B -m vulnprior.cli pilot --config data\pilot_repositories.json --workdir $pilotWork --out data\pilot-2026-04-24
```

The clone workspace was moved to the short Temp path because Git clone failed under the long OneDrive project path.

## Dataset

| Repository | Components | OSV Findings | Namespace-Reachable Findings | Top Priority |
| --- | ---: | ---: | ---: | --- |
| WebGoat/WebGoat | 20 | 38 | 36 | high |
| OWASP-Benchmark/BenchmarkJava | 41 | 18 | 17 | high |
| apache/struts-examples | 48 | 10 | 8 | high |
| Total | 109 | 66 | 61 | high |

Priority labels:

- Critical: 0
- High: 61
- Medium: 0
- Low: 5

Reachability labels:

- Reachable: 61
- Unreachable: 5

## Main Observations

- The first successful pilot produced a non-empty empirical dataset from three real Java/Maven repositories.
- Most findings were marked reachable by namespace-reference evidence, which is useful for a first pass but too broad for the final paper claim.
- WebGoat findings are dominated by `com.thoughtworks.xstream:xstream`.
- BenchmarkJava findings include Spring MVC, Spring Web, Hibernate, Bouncy Castle, and Commons Lang components.
- Struts examples include Log4j, Struts, Jackson, JasperReports, and Shiro findings.

## Current Validity Limits

- This run does not use Syft yet; it uses a direct Maven `pom.xml` parser.
- It does not resolve transitive dependencies, so the dataset is smaller than a full SBOM-based scanner dataset.
- Reachability is namespace-level source-reference analysis, not function-level CodeQL reachability.
- OSV records do not always include CVSS vectors or summaries, so several findings use the ranker's conservative default severity signal.
- No real upstream VEX documents were available in this pilot; VEX status is `unknown` for all findings.

## Next Empirical Step

Replace one layer at a time:

1. Add Syft-generated CycloneDX SBOMs and compare component counts against the Maven parser.
2. Add CodeQL call graph export for one repository and compare function-level reachability against namespace reachability.
3. Add manual labels for the top 25 findings using `data/pilot-2026-04-24/manual-labels-template.csv`.

