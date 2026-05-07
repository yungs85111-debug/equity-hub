"""DB에 저장된 metrics로 tiers/scores를 재계산하여 덮어씁니다.
Usage: python -m backend.services.recompute_tiers
"""
from __future__ import annotations
import sqlite3
import sys
from collections import defaultdict

from backend.config import DB_PATH, FISCAL_YEAR
from backend.services.tiering import calc_all_tiers
from backend.services.scoring import (
    calc_common_score, calc_sector_score, calc_total_score, calc_overall_tier,
)

def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    fy = FISCAL_YEAR

    # 1) metrics + company info 로드
    rows = conn.execute("""
        SELECT c.ticker, c.sector,
               m.gpm, m.opm, m.npm, m.roe, m.roa,
               m.rev_yoy, m.rev_3y_cagr, m.dr, m.icr, m.cr,
               m.asset_turn, m.inv_turn, m.per, m.pbr, m.psr,
               m.ev_ebitda, m.fcf, m.fcf_margin, m.div_yield, m.net_cash
        FROM companies c
        JOIN metrics m ON c.ticker = m.ticker AND m.fiscal_year = ?
    """, (fy,)).fetchall()

    if not rows:
        print(f"ERROR: metrics 테이블에 fiscal_year={fy} 데이터가 없습니다.")
        sys.exit(1)

    METRIC_KEYS = [
        "gpm","opm","npm","roe","roa","rev_yoy","rev_3y_cagr",
        "dr","icr","cr","asset_turn","inv_turn","per","pbr","psr",
        "ev_ebitda","fcf","fcf_margin","div_yield","net_cash",
    ]

    # 섹터별 metrics 그룹화
    by_sector: dict[str, list[dict]] = defaultdict(list)
    all_metrics: dict[str, dict] = {}
    ticker_sector: dict[str, str] = {}

    for row in rows:
        m = {k: row[k] for k in METRIC_KEYS}
        ticker = row["ticker"]
        sector = row["sector"]
        all_metrics[ticker] = m
        by_sector[sector].append(m)
        ticker_sector[ticker] = sector

    # 2) 티어 재계산
    new_tiers: dict[str, dict] = {}
    for ticker, m in all_metrics.items():
        sector = ticker_sector[ticker]
        sector_ms = by_sector[sector]
        new_tiers[ticker] = calc_all_tiers(m, sector_ms)

    # 3) 점수 재계산 (섹터 common_score 목록이 필요하므로 2-pass)
    common_scores: dict[str, float] = {
        t: calc_common_score(new_tiers[t]) for t in new_tiers
    }
    sector_commons: dict[str, list[float]] = defaultdict(list)
    for ticker, cs in common_scores.items():
        sector_commons[ticker_sector[ticker]].append(cs)

    # 4) DB 업데이트
    cur = conn.cursor()
    updated = 0
    for ticker, tiers in new_tiers.items():
        cs = common_scores[ticker]
        ss = calc_sector_score(cs, sector_commons[ticker_sector[ticker]])
        ts = calc_total_score(cs, ss)
        ot = calc_overall_tier(ts)
        sp = ss  # sector_percentile = sector_score

        cur.execute("""INSERT OR REPLACE INTO tiers
            (ticker, fiscal_year, tier_profitability, tier_growth, tier_stability,
             tier_efficiency, tier_valuation, tier_cash_power)
            VALUES (?,?,?,?,?,?,?,?)""", (
            ticker, fy,
            tiers.get("tier_profitability"), tiers.get("tier_growth"),
            tiers.get("tier_stability"), tiers.get("tier_efficiency"),
            tiers.get("tier_valuation"), tiers.get("tier_cash_power"),
        ))
        cur.execute("""INSERT OR REPLACE INTO scores
            (ticker, fiscal_year, common_score, sector_score, total_score,
             overall_tier, sector_percentile)
            VALUES (?,?,?,?,?,?,?)""", (
            ticker, fy, cs, ss, ts, ot, sp,
        ))
        updated += 1

    conn.commit()
    conn.close()
    print(f"OK 티어·점수 재계산 완료: {updated}개 종목 (fiscal_year={fy})")


if __name__ == "__main__":
    main()
