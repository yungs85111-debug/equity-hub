"""6대 코어 스탯 지표 계산 — Skills_core §2."""
from __future__ import annotations


def safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return a / b


def calc_metrics(fin: dict, price: dict, prev_fin: dict | None, prev3_fin: dict | None) -> dict:
    """
    fin       : current year financials
    price     : yfinance supplement dict
    prev_fin  : prior year financials (for YoY)
    prev3_fin : 3-years-ago financials (for CAGR)
    """
    rev  = fin.get("revenue")
    gp   = fin.get("gross_profit")
    oi   = fin.get("operating_income")
    ni   = fin.get("net_income")
    eps  = fin.get("eps_diluted")
    ta   = fin.get("total_assets")
    te   = fin.get("total_equity")
    td   = fin.get("total_debt")
    cash = fin.get("cash")
    inv  = fin.get("inventory")
    ar   = fin.get("accounts_receivable")
    ocf  = fin.get("operating_cashflow")
    cap  = fin.get("capex")
    intx = fin.get("interest_expense")

    sp   = price.get("stock_price")
    mc   = price.get("market_cap")
    per_yf = price.get("per")
    pbr_yf = price.get("pbr")

    # Profitability
    gpm = safe_div(gp, rev)
    opm = safe_div(oi, rev)
    npm = safe_div(ni, rev)
    roe = safe_div(ni, te)
    roa = safe_div(ni, ta)

    # Growth
    prev_rev = prev_fin.get("revenue") if prev_fin else None
    rev_yoy  = safe_div(rev - prev_rev, prev_rev) if (rev and prev_rev) else None

    prev3_rev  = prev3_fin.get("revenue") if prev3_fin else None
    rev_3y_cagr = None
    if rev and prev3_rev and prev3_rev > 0:
        rev_3y_cagr = ((rev / prev3_rev) ** (1 / 3) - 1)

    # Stability — DR uses total_debt / total_equity (NOT book_liabilities)
    dr  = safe_div(td, te)
    icr = safe_div(oi, intx) if intx and intx > 0 else None

    # Current ratio not available from EDGAR facts easily — skip
    cr = None

    # Efficiency
    asset_turn = safe_div(rev, ta)
    inv_turn   = safe_div(rev, inv) if inv and inv > 0 else None

    # Valuation
    ebitda = None
    if oi is not None:
        ebitda = oi  # simplified — depreciation not always available
    ev = (mc + (td or 0) - (cash or 0)) if mc else None
    ev_ebitda = safe_div(ev, ebitda) if ebitda else None
    per = per_yf if per_yf else safe_div(sp, eps)
    pbr = pbr_yf if pbr_yf else safe_div(sp, safe_div(te, mc / sp if sp and mc else None))
    psr = safe_div(mc, rev)

    # Cash flow — FCF = operating_cashflow - capex (Skills §10 Step 7, mandatory)
    fcf = None
    if ocf is not None and cap is not None:
        fcf = ocf - cap
    fcf_margin = safe_div(fcf, rev)

    # Net cash
    net_cash = (cash - (td or 0)) if cash else None

    # Percentage scaling
    def pct(v):
        return round(v * 100, 2) if v is not None else None

    return {
        "gpm":        pct(gpm),
        "opm":        pct(opm),
        "npm":        pct(npm),
        "roe":        pct(roe),
        "roa":        pct(roa),
        "rev_yoy":    pct(rev_yoy),
        "rev_3y_cagr": pct(rev_3y_cagr),
        "dr":         pct(dr),
        "icr":        round(icr, 2) if icr else None,
        "cr":         None,
        "asset_turn": round(asset_turn, 3) if asset_turn else None,
        "inv_turn":   round(inv_turn, 2) if inv_turn else None,
        "per":        round(per, 2) if per else None,
        "pbr":        round(pbr_yf, 2) if pbr_yf else None,
        "psr":        round(psr, 2) if psr else None,
        "ev_ebitda":  round(ev_ebitda, 2) if ev_ebitda else None,
        "fcf":        round(fcf, 0) if fcf else None,
        "fcf_margin": pct(fcf_margin),
        "div_yield":  None,
        "net_cash":   round(net_cash, 0) if net_cash else None,
    }
