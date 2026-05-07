import json
from flask import Blueprint, jsonify, request
import sqlite3
import numpy as np

from backend.config import DB_PATH, FISCAL_YEAR, DATA_DIR

indicator_bp = Blueprint("indicator", __name__)

_META = json.loads((DATA_DIR / "indicator_meta.json").read_text(encoding="utf-8"))

STAT_FOR_METRIC = {
    "opm": "profitability", "roe": "profitability", "gpm": "profitability",
    "rev_yoy": "growth", "rev_3y_cagr": "growth",
    "dr": "stability", "icr": "stability",
    "asset_turn": "efficiency", "inv_turn": "efficiency",
    "per": "valuation", "ev_ebitda": "valuation", "pbr": "valuation",
    "fcf_margin": "cash_power", "fcf": "cash_power",
    "net_cash": "cash_power",
}

REVERSE_METRICS = {"dr", "per", "ev_ebitda"}


def _price_date(conn):
    row = conn.execute("SELECT MAX(price_date) FROM prices").fetchone()
    return row[0] if row else None


@indicator_bp.get("/api/indicator/<ticker>/<indicator_name>")
def get_indicator(ticker: str, indicator_name: str):
    fy = request.args.get("fiscal_year", FISCAL_YEAR, type=int)
    ticker = ticker.upper()
    indicator_name = indicator_name.lower()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    pd = _price_date(conn)

    # Company sector
    co = conn.execute("SELECT sector FROM companies WHERE ticker=?", (ticker,)).fetchone()
    if not co:
        conn.close()
        return jsonify({"error": "Not found"}), 404
    sector = co["sector"]

    # Ticker's value
    m = conn.execute("SELECT * FROM metrics WHERE ticker=? AND fiscal_year=?", (ticker, fy)).fetchone()
    if m is None:
        conn.close()
        return jsonify({"error": "Metrics not found"}), 404

    try:
        current_value = m[indicator_name]
    except Exception:
        current_value = None

    # Tier for this ticker
    t = conn.execute("SELECT * FROM tiers WHERE ticker=? AND fiscal_year=?", (ticker, fy)).fetchone()
    stat = STAT_FOR_METRIC.get(indicator_name)
    tier = None
    if t and stat:
        try:
            tier = t[f"tier_{stat}"]
        except Exception:
            pass

    # Sector distribution
    sector_rows = conn.execute("""
        SELECT m.{col}
        FROM metrics m JOIN companies c ON m.ticker = c.ticker
        WHERE c.sector = ? AND m.fiscal_year = ? AND m.{col} IS NOT NULL
    """.format(col=indicator_name), (sector, fy)).fetchall()
    conn.close()

    vals = [r[0] for r in sector_rows if r[0] is not None]
    n = len(vals)
    sector_avg = round(float(np.mean(vals)), 2) if vals else None
    percentile = None
    lo, hi = None, None
    pcts = {}

    if n >= 10:
        q = np.percentile(vals, [10, 25, 50, 75, 90])
        lo, hi = round(q[1], 2), round(q[3], 2)
        pcts = {f"p{p}": round(q[i], 2) for i, p in enumerate([10, 25, 50, 75, 90])}
        source_mode = "dynamic"
        source_label = f"섹터 중앙값 {round(q[2], 2)} (demo.db 실측 {n}개사, {fy}년 기준)"
        if current_value is not None:
            below = sum(1 for v in vals if v < current_value)
            percentile = round(below / n * 100, 1)
    else:
        source_mode = "fallback"
        source_label = "⚠️ 섹터 데이터 부족 — S&P 500 평균 기준 적용"

    meta = _META.get(indicator_name, {})

    return jsonify({
        "ticker":             ticker,
        "indicator_name":     indicator_name,
        "indicator_fullname": meta.get("fullname", indicator_name.upper()),
        "value":              current_value,
        "tier":               tier,
        "unit":               meta.get("unit", ""),
        "sector":             sector,
        "sector_avg":         sector_avg,
        "lo":                 lo,
        "hi":                 hi,
        "percentile":         percentile,
        "percentiles":        pcts,
        "n":                  n,
        "source_mode":        source_mode,
        "source_label":       source_label,
        "definition":         meta.get("definition", ""),
        "caution_text":       meta.get("caution_text"),
        "price_date":         pd,
        "fiscal_year":        fy,
    })
