from __future__ import annotations

import math


def parse_cvss_base_score(vector: str | None) -> float | None:
    if not vector:
        return None
    if vector.startswith("CVSS:3."):
        return _parse_cvss_v3(vector)
    return None


def _parse_cvss_v3(vector: str) -> float | None:
    metrics = {}
    for part in vector.split("/")[1:]:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        metrics[key] = value

    try:
        av = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}[metrics["AV"]]
        ac = {"L": 0.77, "H": 0.44}[metrics["AC"]]
        pr_scope_u = {"N": 0.85, "L": 0.62, "H": 0.27}
        pr_scope_c = {"N": 0.85, "L": 0.68, "H": 0.5}
        scope_changed = metrics["S"] == "C"
        pr = (pr_scope_c if scope_changed else pr_scope_u)[metrics["PR"]]
        ui = {"N": 0.85, "R": 0.62}[metrics["UI"]]
        c = {"H": 0.56, "L": 0.22, "N": 0.0}[metrics["C"]]
        i = {"H": 0.56, "L": 0.22, "N": 0.0}[metrics["I"]]
        a = {"H": 0.56, "L": 0.22, "N": 0.0}[metrics["A"]]
    except KeyError:
        return None

    impact_subscore = 1 - ((1 - c) * (1 - i) * (1 - a))
    if scope_changed:
        impact = 7.52 * (impact_subscore - 0.029) - 3.25 * ((impact_subscore - 0.02) ** 15)
    else:
        impact = 6.42 * impact_subscore
    exploitability = 8.22 * av * ac * pr * ui
    if impact <= 0:
        return 0.0
    if scope_changed:
        return min(_round_up_1_decimal(1.08 * (impact + exploitability)), 10.0)
    return min(_round_up_1_decimal(impact + exploitability), 10.0)


def _round_up_1_decimal(value: float) -> float:
    return math.ceil(value * 10.0) / 10.0


def severity_label(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score > 0:
        return "low"
    return "none"

