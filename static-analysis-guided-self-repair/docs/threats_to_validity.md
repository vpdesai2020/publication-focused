# Threats to Validity

## Construct Validity

Static analyzers are imperfect proxies for vulnerability presence. The study should report analyzer-specific findings and include manual validation for a stratified sample.

Unit tests and fuzz tests are also incomplete behavior oracles. Functionality preservation should be phrased as preservation under the available tests, not full semantic equivalence.

## Internal Validity

Repairs may remove vulnerable code by deleting required behavior or adding narrow test-specific checks. The repair prompt, patch review rules, and automated guards should explicitly reject test deletion, analyzer suppression, and hard-coded outputs.

## External Validity

Early results on Python SecurityEval-style tasks may not transfer to repository-scale software, compiled languages, or framework-specific vulnerabilities. A journal version should include at least one additional language or repository-style benchmark.

## Reliability

LLM sampling is stochastic. The study should fix model versions, decoding parameters, prompts, analyzer versions, and random seeds where possible. Raw artifacts should be retained for reproduction.

