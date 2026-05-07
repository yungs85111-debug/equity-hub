"""demo_fixture.json → demo.db 일괄 INSERT.
Usage: python -m backend.services.seed_demo
"""
import json
import sqlite3
import sys
from pathlib import Path

from backend.config import DB_PATH, DATA_DIR, FISCAL_YEAR
from backend.db.init_db import main as init_schema

FIXTURE_FILE = DATA_DIR / "demo_fixture.json"


def load_fixture() -> list[dict]:
    if not FIXTURE_FILE.exists():
        print(f"ERROR demo_fixture.json not found at {FIXTURE_FILE}")
        print("Run: DATA_MODE=live python -m backend.services.fetch_edgar")
        sys.exit(1)
    return json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))


def seed(rows: list[dict]) -> None:
    init_schema()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # Determine a common price_date from rows
    price_date = "2023-12-31"
    for r in rows:
        d = r.get("price", {}).get("price_date")
        if d:
            price_date = d
            break

    fy = FISCAL_YEAR

    for r in rows:
        ticker  = r["ticker"]
        fin     = r.get("financials", {})
        price   = r.get("price", {})
        met     = r.get("metrics", {})
        tiers   = r.get("tiers", {})
        scores  = r.get("scores", {})
        insights = r.get("insights", [])
        pd_date = price.get("price_date") or price_date

        cur.execute("""INSERT OR REPLACE INTO companies
            (ticker, name, sector, gics_industry, cik, exchange)
            VALUES (?,?,?,?,?,?)""",
            (ticker, r["name"], r["sector"], None, r.get("cik"), r.get("exchange")))

        cur.execute("""INSERT OR REPLACE INTO financials
            (ticker, fiscal_year, revenue, gross_profit, operating_income, net_income,
             eps_diluted, total_assets, total_equity, total_debt, cash, inventory,
             accounts_receivable, operating_cashflow, capex, interest_expense)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            ticker, fy,
            fin.get("revenue"), fin.get("gross_profit"), fin.get("operating_income"),
            fin.get("net_income"), fin.get("eps_diluted"), fin.get("total_assets"),
            fin.get("total_equity"), fin.get("total_debt"), fin.get("cash"),
            fin.get("inventory"), fin.get("accounts_receivable"),
            fin.get("operating_cashflow"), fin.get("capex"), fin.get("interest_expense"),
        ))

        cur.execute("""INSERT OR REPLACE INTO prices
            (ticker, price_date, stock_price, market_cap, price_change_pct, price_change_1y)
            VALUES (?,?,?,?,?,?)""", (
            ticker, pd_date,
            price.get("stock_price"), price.get("market_cap"),
            price.get("price_change_pct"), price.get("price_change_1y"),
        ))

        cur.execute("""INSERT OR REPLACE INTO metrics
            (ticker, fiscal_year, gpm, opm, npm, roe, roa, rev_yoy, rev_3y_cagr,
             dr, icr, cr, asset_turn, inv_turn, per, pbr, psr, ev_ebitda,
             fcf, fcf_margin, div_yield, net_cash)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            ticker, fy,
            met.get("gpm"), met.get("opm"), met.get("npm"), met.get("roe"), met.get("roa"),
            met.get("rev_yoy"), met.get("rev_3y_cagr"), met.get("dr"), met.get("icr"),
            met.get("cr"), met.get("asset_turn"), met.get("inv_turn"), met.get("per"),
            met.get("pbr"), met.get("psr"), met.get("ev_ebitda"), met.get("fcf"),
            met.get("fcf_margin"), met.get("div_yield"), met.get("net_cash"),
        ))

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
            ticker, fy,
            scores.get("common_score"), scores.get("sector_score"),
            scores.get("total_score"), scores.get("overall_tier"),
            scores.get("sector_percentile"),
        ))

        for seq, ins in enumerate(insights):
            cur.execute("""INSERT OR REPLACE INTO insights
                (ticker, fiscal_year, seq, kind, title, body)
                VALUES (?,?,?,?,?,?)""", (
                ticker, fy, seq,
                ins.get("kind"), ins.get("title"), ins.get("body"),
            ))

    conn.commit()
    conn.close()
    print(f"OK demo.db seeded: {len(rows)} tickers (fiscal_year={fy})")


def main() -> None:
    rows = load_fixture()
    seed(rows)


if __name__ == "__main__":
    main()
