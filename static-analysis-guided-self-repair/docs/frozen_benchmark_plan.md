# Frozen Benchmark Plan

## Goal

Create a frozen Python benchmark subset large enough for a first submission while keeping manual validation feasible for solo work.

## Minimum Size

- 50 tasks.
- 6 to 10 CWE categories.
- 2 to 4 model families.
- 3 repair iterations.
- 3 random seeds where model cost permits.

## Inclusion Criteria

- Prompt is clear and implementable in one file.
- Expected public API is stated.
- Functional tests can be written without external services.
- Security/property tests can exercise the vulnerable behavior.
- At least one external analyzer can plausibly flag the vulnerable pattern.

## Exclusion Criteria

- Ambiguous task behavior.
- Requires network access, cloud credentials, or system-specific services.
- Requires non-standard packages unless the dependency is explicitly vendored or pinned.
- Security property cannot be tested or manually reviewed.

## Suggested CWE Mix

- CWE-022 path traversal.
- CWE-078 command injection.
- CWE-089 SQL injection.
- CWE-094 code injection.
- CWE-327 weak cryptography.
- CWE-330 insufficient randomness.
- CWE-502 unsafe deserialization.
- CWE-601 open redirect.
- CWE-918 SSRF.
- CWE-798 hard-coded credentials.

