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

# 핵심 지표 한국어 전체 명칭
_METRIC_LABEL: dict[str, str] = {
    "roe":         "자기자본수익률(ROE)",
    "opm":         "영업이익률(OPM)",
    "fcf_margin":  "잉여현금흐름마진(FCF Margin)",
    "rev_yoy":     "연간 매출성장률(Rev YoY)",
    "rev_3y_cagr": "3년 매출 CAGR",
    "dr":          "부채비율(DR)",
    "icr":         "이자보상배율(ICR)",
    "asset_turn":  "자산회전율(Asset Turnover)",
    "per":         "주가수익비율(PER)",
    "ev_ebitda":   "EV/EBITDA",
    "pbr":         "주가순자산비율(PBR)",
    "div_yield":   "배당수익률(Dividend Yield)",
}

# 지표 단위 (표시용)
_METRIC_UNIT: dict[str, str] = {
    "roe":         "%",
    "opm":         "%",
    "fcf_margin":  "%",
    "rev_yoy":     "%",
    "rev_3y_cagr": "%",
    "dr":          "%",
    "icr":         "x",
    "asset_turn":  "x",
    "per":         "x",
    "ev_ebitda":   "x",
    "pbr":         "x",
    "div_yield":   "%",
}


# ── §7.1 섹터 인사이트 ────────────────────────────────────────────────────────
def sector_insight(
    tier_dist: dict,
    key_stat: str,
    avg_value: float | None,
    narrative: str = "",
    key_metric_context: dict | None = None,
) -> str:
    """
    tier_dist:         {s_pct, a_pct, b_pct, c_pct}
    key_stat:          primary metric name (e.g. 'roe', 'fcf_margin')
    avg_value:         sector average for key_stat
    narrative:         sector-specific 1-2 sentence description (from sector_definitions.json)
    key_metric_context: {metric_name: explanation_str} for plain-language descriptions
    """
    if key_metric_context is None:
        key_metric_context = {}

    s   = tier_dist.get("s_pct", 0)
    a   = tier_dist.get("a_pct", 0)
    b   = tier_dist.get("b_pct", 0)
    c   = tier_dist.get("c_pct", 0)

    # ── 문장 1: 섹터 특성 ────────────────────────────────────────────────────
    if narrative:
        sent1 = narrative
    elif s >= 30:
        sent1 = f"이 섹터는 S티어 기업이 {s:.0f}%에 달하는 강한 섹터입니다."
    elif c >= 30:
        sent1 = f"이 섹터는 C티어 기업이 {c:.0f}%로 상당수 포함되어 있어 선별적 접근이 필요합니다."
    else:
        sent1 = "이 섹터는 A·B티어 중심의 균형 잡힌 구성을 보입니다."

    # ── 문장 2: 핵심 지표 설명 + 현재 수치 ──────────────────────────────────
    context_str = key_metric_context.get(key_stat, "")
    unit = _METRIC_UNIT.get(key_stat, "")
    label = _METRIC_LABEL.get(key_stat, key_stat)

    if context_str and avg_value is not None:
        sent2 = f"{context_str} 현재 섹터 평균은 {avg_value:.1f}{unit}입니다."
    elif context_str:
        sent2 = context_str
    elif avg_value is not None:
        sent2 = f"섹터 평균 {label}은 {avg_value:.1f}{unit}입니다."
    else:
        sent2 = ""

    # ── 문장 3: 티어 분포 맥락 ───────────────────────────────────────────────
    if s + a >= 50:
        sent3 = "우량 기업(S·A티어)이 절반 이상으로 종목 선택 범위가 비교적 넓습니다."
    elif c >= 40:
        sent3 = "종목 간 실적 편차가 크므로 개별 종목 비교 분석이 특히 중요합니다."
    elif b >= 40:
        sent3 = "중간 수준의 안정적 기업이 주를 이루어 방어적 성격이 강합니다."
    else:
        sent3 = "S~C티어가 고르게 분포해 다양한 투자 목적에 맞는 종목을 찾을 수 있습니다."

    parts = [sent1, sent2, sent3, "종목별 상세는 [종목 비교] 탭에서 확인하세요."]
    return " ".join(p for p in parts if p)


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
