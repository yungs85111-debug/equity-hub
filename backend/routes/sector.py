import json
from flask import Blueprint, jsonify, request
import sqlite3

from backend.config import DB_PATH, FISCAL_YEAR, DATA_DIR
from backend.services.insights import sector_insight
from backend.services.tiering import calc_stat_tier

sector_bp = Blueprint("sector", __name__)

_DEFS = json.loads((DATA_DIR / "sector_definitions.json").read_text(encoding="utf-8"))


def _price_date(conn):
    row = conn.execute("SELECT MAX(price_date) FROM prices").fetchone()
    return row[0] if row else None


def _source_label(n: int, fy: int) -> str:
    if n >= 10:
        return f"demo.db 실측 {n}개사, {fy}년 기준"
    return "⚠️ 섹터 데이터 부족 — S&P 500 평균 기준 적용"


@sector_bp.get("/api/sector/<sector_name>")
def get_sector(sector_name: str):
    fy  = request.args.get("fiscal_year", FISCAL_YEAR, type=int)
    tab = request.args.get("tab", "understand")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    pd = _price_date(conn)

    # Basic sector stats
    tickers = conn.execute(
        "SELECT ticker FROM companies WHERE sector=?", (sector_name,)
    ).fetchall()
    n = len(tickers)
    source_label = _source_label(n, fy)

    # Avg metrics per stat
    avg_row = conn.execute("""
        SELECT
            AVG(m.opm) avg_opm, AVG(m.roe) avg_roe,
            AVG(m.rev_yoy) avg_rev_yoy, AVG(m.rev_3y_cagr) avg_cagr,
            AVG(m.dr) avg_dr, AVG(m.icr) avg_icr,
            AVG(m.asset_turn) avg_asset_turn,
            AVG(m.per) avg_per, AVG(m.ev_ebitda) avg_ev_ebitda,
            AVG(m.fcf_margin) avg_fcf_margin
        FROM metrics m
        JOIN companies c ON m.ticker = c.ticker
        WHERE c.sector = ? AND m.fiscal_year = ?
    """, (sector_name, fy)).fetchone()

    # Tier distribution
    dist = conn.execute("""
        SELECT
            COUNT(*) n,
            SUM(CASE WHEN sc.overall_tier='S' THEN 1 ELSE 0 END) n_s,
            SUM(CASE WHEN sc.overall_tier='A' THEN 1 ELSE 0 END) n_a,
            SUM(CASE WHEN sc.overall_tier='B' THEN 1 ELSE 0 END) n_b,
            SUM(CASE WHEN sc.overall_tier='C' THEN 1 ELSE 0 END) n_c
        FROM scores sc
        JOIN companies c ON sc.ticker = c.ticker
        WHERE c.sector = ? AND sc.fiscal_year = ?
    """, (sector_name, fy)).fetchone()

    dn = dist["n"] or 1
    tier_dist = {
        "n": dist["n"], "n_s": dist["n_s"] or 0, "n_a": dist["n_a"] or 0,
        "n_b": dist["n_b"] or 0, "n_c": dist["n_c"] or 0,
        "s_pct": round((dist["n_s"] or 0) / dn * 100, 1),
        "a_pct": round((dist["n_a"] or 0) / dn * 100, 1),
        "b_pct": round((dist["n_b"] or 0) / dn * 100, 1),
        "c_pct": round((dist["n_c"] or 0) / dn * 100, 1),
    }

    defs = _DEFS.get(sector_name, {})
    key_indicators = defs.get("key_indicators", ["opm", "roe", "rev_yoy"])

    def _r(v):
        return round(v, 2) if v is not None else None

    # 전체 종목 metrics — 섹터 평균을 글로벌 기준으로 티어링하기 위해 사용
    all_metrics_rows = conn.execute(
        "SELECT * FROM metrics WHERE fiscal_year = ?", (fy,)
    ).fetchall()
    all_metrics_list = [dict(r) for r in all_metrics_rows]

    # 섹터 평균값을 하나의 "가상 회사"로 취급해 tiering
    avg_metrics_dict = {
        "opm": avg_row["avg_opm"], "roe": avg_row["avg_roe"],
        "rev_yoy": avg_row["avg_rev_yoy"], "rev_3y_cagr": avg_row["avg_cagr"],
        "dr": avg_row["avg_dr"], "icr": avg_row["avg_icr"],
        "asset_turn": avg_row["avg_asset_turn"],
        "per": avg_row["avg_per"], "ev_ebitda": avg_row["avg_ev_ebitda"],
        "fcf_margin": avg_row["avg_fcf_margin"],
    }
    stat_tiers = {
        stat: calc_stat_tier(stat, avg_metrics_dict, all_metrics_list)
        for stat in ["profitability", "growth", "stability", "efficiency", "valuation", "cash_power"]
    }

    avg_stats = {
        "profitability": {"opm": _r(avg_row["avg_opm"]), "roe": _r(avg_row["avg_roe"]), "tier": stat_tiers["profitability"], "source": source_label},
        "growth":        {"rev_yoy": _r(avg_row["avg_rev_yoy"]), "cagr": _r(avg_row["avg_cagr"]), "tier": stat_tiers["growth"], "source": source_label},
        "stability":     {"dr": _r(avg_row["avg_dr"]), "icr": _r(avg_row["avg_icr"]), "tier": stat_tiers["stability"], "source": source_label},
        "efficiency":    {"asset_turn": _r(avg_row["avg_asset_turn"]), "tier": stat_tiers["efficiency"], "source": source_label},
        "valuation":     {"per": _r(avg_row["avg_per"]), "ev_ebitda": _r(avg_row["avg_ev_ebitda"]), "tier": stat_tiers["valuation"], "source": source_label},
        "cash_power":    {"fcf_margin": _r(avg_row["avg_fcf_margin"]), "tier": stat_tiers["cash_power"], "source": source_label},
    }

    # key indicator details
    metric_col_map = {
        "opm": "avg_opm", "roe": "avg_roe", "rev_yoy": "avg_rev_yoy",
        "dr": "avg_dr", "icr": "avg_icr", "asset_turn": "avg_asset_turn",
        "per": "avg_per", "ev_ebitda": "avg_ev_ebitda", "fcf_margin": "avg_fcf_margin",
        "fcf_margin": "avg_fcf_margin",
    }
    key_ind_details = []
    for ki in key_indicators:
        col = metric_col_map.get(ki)
        avg_val = _r(avg_row[col]) if col and avg_row[col] is not None else None
        key_ind_details.append({"indicator": ki, "sector_avg": avg_val, "source": source_label})

    auto_insight = sector_insight(
        tier_dist,
        key_indicators[0] if key_indicators else "opm",
        key_ind_details[0]["sector_avg"] if key_ind_details else None,
    )

    # 전체 섹터 common_score 순위 기반 overall_tier (sectors.py와 동일 로직)
    all_sector_commons = conn.execute("""
        SELECT c.sector, AVG(sc.common_score) avg_common
        FROM companies c JOIN scores sc ON c.ticker = sc.ticker AND sc.fiscal_year = ?
        GROUP BY c.sector
        ORDER BY avg_common DESC
    """, (fy,)).fetchall()

    this_common = avg_metrics_dict  # avg_common_score for this sector
    this_sector_common = next(
        (r["avg_common"] for r in all_sector_commons if r["sector"] == sector_name), None
    )
    sector_commons_list = [r["avg_common"] for r in all_sector_commons if r["avg_common"] is not None]
    n_sectors = len(sector_commons_list)

    if this_sector_common is not None and n_sectors > 1:
        rank = sorted(sector_commons_list, reverse=True).index(this_sector_common)
        pct_rank = rank / max(n_sectors - 1, 1)
        if pct_rank <= 0.18:   overall_tier = "S"
        elif pct_rank <= 0.45: overall_tier = "A"
        elif pct_rank <= 0.75: overall_tier = "B"
        else:                  overall_tier = "C"
    else:
        overall_tier = "B"

    result = {
        "sector": sector_name,
        "n": n,
        "fiscal_year": fy,
        "price_date": pd,
        "sector_intro": defs.get("intro", ""),
        "key_indicators": key_indicators,
        "key_indicator_details": key_ind_details,
        "avg_stats": avg_stats,
        "tier_dist": tier_dist,
        "auto_insight": auto_insight,
        "source_label": source_label,
        "overall_tier": overall_tier,
    }

    if tab == "compare":
        # Heatmap top 20 by market cap
        top20_rows = conn.execute("""
            SELECT c.ticker, c.name,
                   p.market_cap,
                   t.tier_profitability, t.tier_growth, t.tier_stability,
                   t.tier_efficiency,    t.tier_valuation, t.tier_cash_power,
                   sc.total_score, sc.overall_tier,
                   m.rev_3y_cagr, m.roe, m.per
            FROM companies c
            JOIN scores  sc ON c.ticker = sc.ticker AND sc.fiscal_year = ?
            JOIN tiers   t  ON c.ticker = t.ticker  AND t.fiscal_year  = ?
            JOIN metrics m  ON c.ticker = m.ticker  AND m.fiscal_year  = ?
            LEFT JOIN prices p ON c.ticker = p.ticker AND p.price_date = ?
            WHERE c.sector = ?
            ORDER BY p.market_cap DESC NULLS LAST
            LIMIT 20
        """, (fy, fy, fy, pd, sector_name)).fetchall()

        top20 = [dict(r) for r in top20_rows]

        # Sector avg row
        avg_tiers_row = conn.execute("""
            SELECT
                GROUP_CONCAT(t.tier_profitability) tp,
                GROUP_CONCAT(t.tier_growth) tg,
                GROUP_CONCAT(t.tier_stability) ts,
                GROUP_CONCAT(t.tier_efficiency) te,
                GROUP_CONCAT(t.tier_valuation) tv,
                GROUP_CONCAT(t.tier_cash_power) tc
            FROM tiers t
            JOIN companies c ON t.ticker = c.ticker
            WHERE c.sector = ? AND t.fiscal_year = ?
        """, (sector_name, fy)).fetchone()

        def _mode_tier(csv_str):
            if not csv_str: return "B"
            vals = csv_str.split(",")
            return max(set(vals), key=vals.count)

        sector_avg_row = {
            "ticker": "SECTOR_AVG", "name": "섹터 평균",
            "tier_profitability": _mode_tier(avg_tiers_row["tp"]),
            "tier_growth":        _mode_tier(avg_tiers_row["tg"]),
            "tier_stability":     _mode_tier(avg_tiers_row["ts"]),
            "tier_efficiency":    _mode_tier(avg_tiers_row["te"]),
            "tier_valuation":     _mode_tier(avg_tiers_row["tv"]),
            "tier_cash_power":    _mode_tier(avg_tiers_row["tc"]),
            "total_score": None, "overall_tier": None, "market_cap": None,
        }

        # CAGR top 3
        cagr_rows = conn.execute("""
            SELECT c.ticker, c.name, m.rev_3y_cagr
            FROM metrics m JOIN companies c ON m.ticker = c.ticker
            WHERE c.sector = ? AND m.fiscal_year = ? AND m.rev_3y_cagr IS NOT NULL
            ORDER BY m.rev_3y_cagr DESC LIMIT 3
        """, (sector_name, fy)).fetchall()

        # ROE vs PER scatter
        scatter_rows = conn.execute("""
            SELECT c.ticker, m.roe, m.per
            FROM metrics m JOIN companies c ON m.ticker = c.ticker
            WHERE c.sector = ? AND m.fiscal_year = ?
              AND m.roe IS NOT NULL AND m.per IS NOT NULL AND m.per > 0
        """, (sector_name, fy)).fetchall()

        result["top20"] = top20
        result["sector_avg_row"] = sector_avg_row
        result["cagr_top3"] = [dict(r) for r in cagr_rows]
        result["scatter"] = [{"ticker": r["ticker"], "roe": r["roe"], "per": r["per"]} for r in scatter_rows]

    conn.close()
    return jsonify(result)
