"""Tier판정 — Skills_core §4.0 분위수(n≥10) / §4.1 절대값 fallback."""
from __future__ import annotations

import numpy as np

# ── §4.1 절대값 fallback (섹터 무관 공통 기준) ─────────────────────────────
FALLBACK: dict[str, dict] = {
    "opm":        {"s": 25,  "a": 15,  "b": 5},
    "roe":        {"s": 25,  "a": 15,  "b": 5},
    "rev_yoy":    {"s": 20,  "a": 10,  "b": 0},
    "rev_3y_cagr":{"s": 15,  "a": 8,   "b": 0},
    "dr":         {"s": 50,  "a": 100, "b": 200, "reverse": True},  # lower is better
    "icr":        {"s": 10,  "a": 5,   "b": 2},
    "asset_turn": {"s": 1.5, "a": 1.0, "b": 0.5},
    "per":        {"s": 20,  "a": 30,  "b": 45,  "reverse": True},  # 2025 시장 기준 상향
    "ev_ebitda":  {"s": 12,  "a": 18,  "b": 25,  "reverse": True},  # 2025 시장 기준 상향
    "fcf_margin": {"s": 15,  "a": 8,   "b": 2},
}

STAT_METRIC_MAP: dict[str, list[str]] = {
    "profitability": ["opm", "roe"],
    "growth":        ["rev_yoy", "rev_3y_cagr"],
    "stability":     ["dr", "icr"],
    "efficiency":    ["asset_turn"],
    "valuation":     ["per", "ev_ebitda"],
    "cash_power":    ["fcf_margin"],
}


def _assign_tier_abs(value: float, thresholds: dict) -> str:
    rev = thresholds.get("reverse", False)
    s, a, b = thresholds["s"], thresholds["a"], thresholds["b"]
    if rev:
        if value <= s: return "S"
        if value <= a: return "A"
        if value <= b: return "B"
        return "C"
    else:
        if value >= s: return "S"
        if value >= a: return "A"
        if value >= b: return "B"
        return "C"


def _assign_tier_percentile(value: float, pcts: np.ndarray) -> str:
    p10, p25, p75, p90 = pcts[0], pcts[1], pcts[3], pcts[4]
    if value >= p90: return "S"
    if value >= p75: return "A"
    if value >= p25: return "B"
    return "C"


def _assign_tier_for_metric(metric: str, value: float | None,
                             sector_vals: list[float] | None,
                             reverse: bool = False) -> str:
    """Return tier string. reverse=True means lower is better."""
    if value is None:
        return "UNKNOWN"

    # Special cases
    if metric == "dr":
        if value == 0:
            return "DEBT-FREE"
        if value > 500:
            return "IMPAIRED"
        reverse = True

    if metric == "icr" and value < 1:
        return "IMPAIRED"

    # §4.0 dynamic
    if sector_vals and len(sector_vals) >= 10:
        clean = [v for v in sector_vals if v is not None]
        if len(clean) >= 10:
            if reverse:
                # 낮을수록 좋은 지표: 값을 부정하여 percentile 계산 후 비교
                neg_clean = [-v for v in clean]
                q = np.percentile(neg_clean, [10, 25, 50, 75, 90])
                return _assign_tier_percentile(-value, q)
            q = np.percentile(clean, [10, 25, 50, 75, 90])
            return _assign_tier_percentile(value, q)

    # §4.1 fallback
    thresholds = FALLBACK.get(metric)
    if thresholds:
        t = dict(thresholds)
        if reverse and "reverse" not in t:
            t["reverse"] = True
        return _assign_tier_abs(value, t)

    return "UNKNOWN"


def calc_stat_tier(stat: str, metrics: dict, sector_metrics: list[dict]) -> str:
    """
    Return the dominant tier for a 6-stat group.
    Priority: IMPAIRED > lower tier > mode.
    """
    metric_keys = STAT_METRIC_MAP.get(stat, [])
    tier_votes: list[str] = []

    for mk in metric_keys:
        v = metrics.get(mk)
        vals = [m.get(mk) for m in sector_metrics if m.get(mk) is not None]
        rev = mk in ("dr", "per", "ev_ebitda")
        t = _assign_tier_for_metric(mk, v, vals, reverse=rev)
        tier_votes.append(t)

    if not tier_votes:
        return "UNKNOWN"
    if "IMPAIRED" in tier_votes:
        return "IMPAIRED"

    order = ["C", "B", "A", "S", "DEBT-FREE", "UNKNOWN"]
    # Most common tier; tie → lower tier wins
    counted = {t: tier_votes.count(t) for t in set(tier_votes)}
    max_count = max(counted.values())
    candidates = [t for t, c in counted.items() if c == max_count]
    for t in order:
        if t in candidates:
            return t
    return tier_votes[0]


def calc_all_tiers(metrics: dict, sector_metrics: list[dict]) -> dict:
    return {
        "tier_profitability": calc_stat_tier("profitability", metrics, sector_metrics),
        "tier_growth":        calc_stat_tier("growth",        metrics, sector_metrics),
        "tier_stability":     calc_stat_tier("stability",     metrics, sector_metrics),
        "tier_efficiency":    calc_stat_tier("efficiency",    metrics, sector_metrics),
        "tier_valuation":     calc_stat_tier("valuation",     metrics, sector_metrics),
        "tier_cash_power":    calc_stat_tier("cash_power",    metrics, sector_metrics),
    }
