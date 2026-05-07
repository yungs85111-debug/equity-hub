"""점수·Overall 티어 — Skills_core §3."""
from __future__ import annotations

TIER_SCORE: dict[str, float] = {
    "S": 100, "A": 75, "B": 50, "C": 25,
    "IMPAIRED": 0, "DEBT-FREE": 75, "UNKNOWN": 50,
}

STAT_WEIGHT: dict[str, float] = {
    "profitability": 0.25,
    "growth":        0.20,
    "stability":     0.20,
    "efficiency":    0.10,
    "valuation":     0.15,
    "cash_power":    0.10,
}

OVERALL_THRESHOLDS = {"S": 80, "A": 65, "B": 45}


def calc_common_score(tiers: dict) -> float:
    total, weight = 0.0, 0.0
    for stat, w in STAT_WEIGHT.items():
        t = tiers.get(f"tier_{stat}", "UNKNOWN")
        total += TIER_SCORE.get(t, 50) * w
        weight += w
    return round(total / weight, 2) if weight else 0.0


def calc_sector_score(common_score: float, sector_common_scores: list[float]) -> float:
    """Percentile of this company within sector, scaled 0-100."""
    clean = [s for s in sector_common_scores if s is not None]
    if not clean:
        return 50.0
    below = sum(1 for s in clean if s < common_score)
    pct = below / len(clean) * 100
    return round(pct, 2)


def calc_total_score(common: float, sector: float) -> float:
    return round(common * 0.4 + sector * 0.6, 2)


def calc_overall_tier(total_score: float) -> str:
    if total_score >= OVERALL_THRESHOLDS["S"]: return "S"
    if total_score >= OVERALL_THRESHOLDS["A"]: return "A"
    if total_score >= OVERALL_THRESHOLDS["B"]: return "B"
    return "C"
