"""자동 인사이트 생성 — Skills_ui §7.1~§7.3."""
from __future__ import annotations

STAT_LABEL_KO = {
    "profitability": "수익성",
    "growth":        "성장성",
    "stability":     "안정성",
    "efficiency":    "효율성",
    "valuation":     "밸류에이션",
    "cash_power":    "현금창출력",
}


# ── §7.1 섹터 인사이트 ────────────────────────────────────────────────────────
def sector_insight(tier_dist: dict, key_stat: str, avg_value: float | None) -> str:
    """
    tier_dist: {s_pct, a_pct, b_pct, c_pct}
    key_stat:  dominant stat label (e.g. 'roe', 'fcf_margin')
    avg_value: sector average for key_stat
    """
    s = tier_dist.get("s_pct", 0)
    c = tier_dist.get("c_pct", 0)

    if s >= 30:
        base = f"이 섹터는 S티어 기업이 {s:.0f}%에 달하는 강한 섹터입니다."
    elif c >= 30:
        base = f"이 섹터는 C티어 기업이 {c:.0f}%로 상당수 포함되어 있어 선별적 접근이 필요합니다."
    else:
        base = "이 섹터는 A·B티어 중심의 균형 잡힌 구성을 보입니다."

    if avg_value is not None:
        stat_ko = STAT_LABEL_KO.get(key_stat, key_stat)
        base += f" 섹터 평균 {stat_ko}은 {avg_value:.1f}%입니다."

    base += " 종목별 상세는 [종목 비교] 탭에서 확인하세요."
    return base


# ── §7.2 기업 인사이트 (강점/약점) ────────────────────────────────────────────
def _tier_label(tier: str) -> str:
    labels = {"S": "최상위", "A": "우수", "B": "보통", "C": "하위"}
    return labels.get(tier, tier)


def company_strength_weakness(tiers: dict, sector_percentile: float) -> list[dict]:
    """Return strength and weakness insight items."""
    insights = []
    stat_tiers = [
        ("profitability", tiers.get("tier_profitability", "UNKNOWN")),
        ("growth",        tiers.get("tier_growth", "UNKNOWN")),
        ("stability",     tiers.get("tier_stability", "UNKNOWN")),
        ("efficiency",    tiers.get("tier_efficiency", "UNKNOWN")),
        ("valuation",     tiers.get("tier_valuation", "UNKNOWN")),
        ("cash_power",    tiers.get("tier_cash_power", "UNKNOWN")),
    ]

    strengths = [(s, t) for s, t in stat_tiers if t in ("S", "A")]
    weaknesses = [(s, t) for s, t in stat_tiers if t in ("C", "IMPAIRED")]

    if strengths:
        top = strengths[0]
        stat_ko = STAT_LABEL_KO[top[0]]
        insights.append({
            "kind": "strength",
            "title": f"강점: {stat_ko} {_tier_label(top[1])}",
            "body": (
                f"{stat_ko}에서 섹터 {_tier_label(top[1])} 수준을 기록하고 있습니다. "
                f"전체 섹터 내 상위 {100 - sector_percentile:.0f}% 수준입니다."
            ),
        })

    if weaknesses:
        bot = weaknesses[0]
        stat_ko = STAT_LABEL_KO[bot[0]]
        insights.append({
            "kind": "caution",
            "title": f"주의: {stat_ko} 하위",
            "body": (
                f"{stat_ko}이 섹터 하위권입니다. "
                "이 지표의 개선 여부를 추적해보세요."
            ),
        })

    return insights


# ── §7.3 정성 인사이트 ────────────────────────────────────────────────────────
def company_qualitative(overall_tier: str, sector_percentile: float) -> dict:
    if overall_tier == "S":
        body = (
            f"종합 점수 기준 섹터 상위 {100 - sector_percentile:.0f}% 이내의 우량 기업입니다. "
            "하지만 높은 밸류에이션이 동반될 수 있으니 매수 가격에 유의하세요."
        )
    elif overall_tier == "A":
        body = (
            "전반적으로 안정적인 펀더멘털을 보유한 기업입니다. "
            "성장 모멘텀과 배당 정책을 함께 살펴보세요."
        )
    elif overall_tier == "C":
        body = (
            "현재 여러 지표에서 개선이 필요한 상태입니다. "
            "구조적 변화나 턴어라운드 신호를 확인한 후 판단하세요."
        )
    else:
        body = (
            "중간 수준의 펀더멘털을 보유합니다. "
            "핵심 지표의 추세 변화를 주목하세요."
        )
    return {"kind": "qualitative", "title": "종합 평가", "body": body}


def generate_company_insights(tiers: dict, overall_tier: str, sector_percentile: float) -> list[dict]:
    items = company_strength_weakness(tiers, sector_percentile)
    items.append(company_qualitative(overall_tier, sector_percentile))
    return items[:3]
