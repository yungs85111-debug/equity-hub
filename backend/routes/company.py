from flask import Blueprint, jsonify, request
import sqlite3

from backend.config import DB_PATH, FISCAL_YEAR
from backend.services.insights import generate_company_insights

company_bp = Blueprint("company", __name__)


@company_bp.get("/api/company/<ticker>")
def get_company(ticker: str):
    fy = request.args.get("fiscal_year", FISCAL_YEAR, type=int)
    ticker = ticker.upper()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    pd_row = conn.execute("SELECT MAX(price_date) FROM prices").fetchone()
    price_date = pd_row[0] if pd_row else None

    # Company profile
    co = conn.execute("SELECT * FROM companies WHERE ticker=?", (ticker,)).fetchone()
    if not co:
        conn.close()
        return jsonify({"error": "Not found"}), 404

    m = conn.execute("SELECT * FROM metrics WHERE ticker=? AND fiscal_year=?", (ticker, fy)).fetchone()
    t = conn.execute("SELECT * FROM tiers WHERE ticker=? AND fiscal_year=?", (ticker, fy)).fetchone()
    sc = conn.execute("SELECT * FROM scores WHERE ticker=? AND fiscal_year=?", (ticker, fy)).fetchone()
    pr = conn.execute("SELECT * FROM prices WHERE ticker=? AND price_date=?", (ticker, price_date)).fetchone()
    ins_rows = conn.execute(
        "SELECT * FROM insights WHERE ticker=? AND fiscal_year=? ORDER BY seq", (ticker, fy)
    ).fetchall()

    conn.close()

    def _v(row, key):
        if row is None: return None
        try: return row[key]
        except Exception: return None

    tiers_dict = {
        "tier_profitability": _v(t, "tier_profitability"),
        "tier_growth":        _v(t, "tier_growth"),
        "tier_stability":     _v(t, "tier_stability"),
        "tier_efficiency":    _v(t, "tier_efficiency"),
        "tier_valuation":     _v(t, "tier_valuation"),
        "tier_cash_power":    _v(t, "tier_cash_power"),
    }

    overall_tier     = _v(sc, "overall_tier") or "B"
    total_score      = _v(sc, "total_score") or 50
    sector_percentile = _v(sc, "sector_percentile") or 50

    # Re-generate insights if DB rows are empty
    if ins_rows:
        insights = [{"kind": r["kind"], "title": r["title"], "body": r["body"]} for r in ins_rows]
    else:
        insights = generate_company_insights(tiers_dict, overall_tier, sector_percentile)

    # TIER_SCORE map for bar width calculation
    TIER_SCORE = {"S": 100, "A": 75, "B": 50, "C": 25, "IMPAIRED": 0, "DEBT-FREE": 75, "UNKNOWN": 50}

    def _stat(stat_key, tier_key, *metric_keys):
        tier = tiers_dict.get(tier_key, "UNKNOWN")
        values = {}
        if m:
            for mk in metric_keys:
                try: values[mk] = m[mk]
                except Exception: values[mk] = None
        return {
            "stat": stat_key,
            "tier": tier,
            "bar_width": TIER_SCORE.get(tier, 50),
            "values": values,
        }

    six_core = [
        _stat("profitability", "tier_profitability", "opm", "roe"),
        _stat("growth",        "tier_growth",        "rev_yoy", "rev_3y_cagr"),
        _stat("stability",     "tier_stability",     "dr", "icr"),
        _stat("efficiency",    "tier_efficiency",    "asset_turn"),
        _stat("valuation",     "tier_valuation",     "per", "ev_ebitda"),
        _stat("cash_power",    "tier_cash_power",    "fcf_margin"),
    ]

    kpis = [
        {"label": "매출 YoY", "value": _v(m, "rev_yoy"),    "unit": "%", "indicator": "rev_yoy"},
        {"label": "OPM",     "value": _v(m, "opm"),        "unit": "%", "indicator": "opm"},
        {"label": "ROE",     "value": _v(m, "roe"),        "unit": "%", "indicator": "roe"},
        {"label": "순현금",   "value": _v(m, "net_cash"),   "unit": "$", "indicator": "net_cash"},
    ]

    return jsonify({
        "ticker":       ticker,
        "name":         _v(co, "name"),
        "sector":       _v(co, "sector"),
        "exchange":     _v(co, "exchange"),
        "gics_industry":_v(co, "gics_industry"),
        "cik":          _v(co, "cik"),
        "fiscal_year":  fy,
        "price_date":   price_date,
        "stock_price":  _v(pr, "stock_price"),
        "market_cap":   _v(pr, "market_cap"),
        "price_change_1y": _v(pr, "price_change_1y"),
        "total_score":  total_score,
        "overall_tier": overall_tier,
        "sector_percentile": sector_percentile,
        "tiers":        tiers_dict,
        "six_core":     six_core,
        "kpis":         kpis,
        "insights":     insights,
    })
