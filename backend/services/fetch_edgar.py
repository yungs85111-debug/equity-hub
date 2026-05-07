"""EDGAR 1회 실측 → demo_fixture.json — Skills_core §10 Step 1~13.
Usage: DATA_MODE=live python -m backend.services.fetch_edgar
"""
import json
import sys
from pathlib import Path

from backend.config import DATA_DIR, FISCAL_YEAR, DATA_MODE
from backend.services.edgar import get_companyfacts
from backend.services.xbrl_map import pick_value, XBRL_MAP
from backend.services.yf_supplement import get_price_data
from backend.services.metrics import calc_metrics
from backend.services.tiering import calc_all_tiers
from backend.services.scoring import (
    calc_common_score, calc_sector_score, calc_total_score, calc_overall_tier,
)
from backend.services.insights import generate_company_insights

TICKERS_FILE = DATA_DIR / "tickers_165.json"
FIXTURE_FILE = DATA_DIR / "demo_fixture.json"

FIN_KEYS = list(XBRL_MAP.keys())


def fetch_one(entry: dict, fiscal_year: int) -> dict | None:
    ticker = entry["ticker"]
    cik    = entry.get("cik", "")
    sector = entry["sector"]
    name   = entry["name"]

    try:
        facts = get_companyfacts(cik)
    except Exception as exc:
        print(f"  WARN EDGAR fail {ticker}: {exc}", file=sys.stderr)
        return None

    def pick(key):
        return pick_value(facts, key, fiscal_year)

    fin = {k: pick(k) for k in FIN_KEYS}
    prev_fin  = {k: pick_value(facts, k, fiscal_year - 1) for k in ["revenue"]}
    prev3_fin = {k: pick_value(facts, k, fiscal_year - 3) for k in ["revenue"]}
    price     = get_price_data(ticker)

    m = calc_metrics(fin, price, prev_fin, prev3_fin)

    return {
        "ticker":      ticker,
        "name":        name,
        "sector":      sector,
        "cik":         cik,
        "exchange":    entry.get("exchange", ""),
        "fiscal_year": fiscal_year,
        "financials":  fin,
        "price":       price,
        "metrics":     m,
    }


def main() -> None:
    if DATA_MODE != "live":
        print("Set DATA_MODE=live to run EDGAR collection.")
        sys.exit(1)

    spec = json.loads(TICKERS_FILE.read_text(encoding="utf-8"))
    tickers = spec["tickers"]
    fy      = spec.get("fiscal_year", FISCAL_YEAR)

    rows: list[dict] = []
    for i, entry in enumerate(tickers, 1):
        ticker = entry["ticker"]
        print(f"[{i}/{len(tickers)}] {ticker} collecting...")
        row = fetch_one(entry, fy)
        if row:
            rows.append(row)

    # ── post-processing: tiers + scores ─────────────────────────────────────
    # Group by sector for peer comparison
    by_sector: dict[str, list[dict]] = {}
    for r in rows:
        by_sector.setdefault(r["sector"], []).append(r)

    for r in rows:
        sector_peers = by_sector[r["sector"]]
        sector_metrics = [p["metrics"] for p in sector_peers]
        r["tiers"] = calc_all_tiers(r["metrics"], sector_metrics)

    for r in rows:
        sector_peers = by_sector[r["sector"]]
        r["common_score"] = calc_common_score(r["tiers"])

    for r in rows:
        sector_peers = by_sector[r["sector"]]
        sector_commons = [p["common_score"] for p in sector_peers]
        sector_score  = calc_sector_score(r["common_score"], sector_commons)
        total_score   = calc_total_score(r["common_score"], sector_score)
        overall_tier  = calc_overall_tier(total_score)
        sector_pct    = sector_score

        r["scores"] = {
            "common_score":      r["common_score"],
            "sector_score":      sector_score,
            "total_score":       total_score,
            "overall_tier":      overall_tier,
            "sector_percentile": sector_pct,
        }
        r["insights"] = generate_company_insights(r["tiers"], overall_tier, sector_pct)

    # Save fixture
    FIXTURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(rows)} tickers saved to {FIXTURE_FILE}")


if __name__ == "__main__":
    main()
