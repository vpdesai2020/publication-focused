from __future__ import annotations

import math


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p_hat = successes / total
    denominator = 1 + z**2 / total
    centre = p_hat + z**2 / (2 * total)
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total)
    lower = (centre - margin) / denominator
    upper = (centre + margin) / denominator
    return max(0.0, lower), min(1.0, upper)


def sign_test_two_sided(wins: int, losses: int) -> float:
    trials = wins + losses
    if trials == 0:
        return 1.0
    smaller = min(wins, losses)
    probability = 0.0
    for k in range(smaller + 1):
        probability += math.comb(trials, k) * (0.5**trials)
    return min(1.0, 2 * probability)

