from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass


OSV_QUERY_BATCH_URL = "https://api.osv.dev/v1/querybatch"


@dataclass(frozen=True, slots=True)
class OsvPackageQuery:
    name: str
    ecosystem: str
    version: str


def query_batch(packages: list[OsvPackageQuery], timeout_seconds: int = 30) -> dict:
    """Query OSV's batch API using only Python standard library modules."""
    body = {
        "queries": [
            {
                "version": package.version,
                "package": {
                    "name": package.name,
                    "ecosystem": package.ecosystem,
                },
            }
            for package in packages
        ]
    }
    request = urllib.request.Request(
        OSV_QUERY_BATCH_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def query_batch_chunked(
    packages: list[OsvPackageQuery],
    chunk_size: int = 100,
    timeout_seconds: int = 30,
) -> list[dict]:
    results = []
    for start in range(0, len(packages), chunk_size):
        chunk = packages[start : start + chunk_size]
        response = query_batch(chunk, timeout_seconds)
        results.extend(response.get("results", [{} for _ in chunk]))
    if len(results) < len(packages):
        results.extend({} for _ in range(len(packages) - len(results)))
    return results

