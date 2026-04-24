from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .models import VexStatus


@dataclass(frozen=True, slots=True)
class VexStatement:
    vulnerability_id: str
    product_ids: tuple[str, ...]
    status: VexStatus
    justification: str | None
    author: str | None
    timestamp: str | None


def load_openvex(path: Path) -> list[VexStatement]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    author = payload.get("author")
    statements = []
    for statement in payload.get("statements", []):
        vulnerability = statement.get("vulnerability", {})
        vulnerability_id = vulnerability.get("name") or vulnerability.get("@id")
        if not vulnerability_id:
            continue
        product_ids = tuple(
            product.get("@id", "")
            for product in statement.get("products", [])
            if product.get("@id")
        )
        statements.append(
            VexStatement(
                vulnerability_id=vulnerability_id,
                product_ids=product_ids,
                status=_status(statement.get("status")),
                justification=statement.get("justification"),
                author=author,
                timestamp=statement.get("timestamp") or payload.get("timestamp"),
            )
        )
    return statements


def match_vex_statement(
    vulnerability_id: str,
    package_url: str,
    statements: list[VexStatement],
) -> VexStatement | None:
    for statement in statements:
        if statement.vulnerability_id != vulnerability_id:
            continue
        if not statement.product_ids or package_url in statement.product_ids:
            return statement
    return None


def _status(value: str | None) -> VexStatus:
    if value == "not_affected":
        return VexStatus.NOT_AFFECTED
    if value == "under_investigation":
        return VexStatus.UNDER_INVESTIGATION
    if value == "fixed":
        return VexStatus.FIXED
    if value == "affected":
        return VexStatus.AFFECTED
    return VexStatus.UNKNOWN

