"""XBRL tag priority mapping — Skills_core §1 tag list."""

# Each key maps to an ordered list of XBRL tags (first match wins)
XBRL_MAP: dict[str, list[str]] = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "NetSales",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "eps_diluted": [
        "EarningsPerShareDiluted",
        "EarningsPerShareBasic",
    ],
    "total_assets": [
        "Assets",
    ],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "total_debt": [
        "LongTermDebt",
        "LongTermDebtAndCapitalLeaseObligations",
        "DebtCurrent",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsAndShortTermInvestments",
    ],
    "inventory": [
        "InventoryNet",
    ],
    "accounts_receivable": [
        "AccountsReceivableNetCurrent",
    ],
    "operating_cashflow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "CapitalExpendituresIncurredButNotYetPaid",
    ],
    "interest_expense": [
        "InterestExpense",
        "InterestAndDebtExpense",
    ],
}


def pick_value(facts: dict, metric_key: str, fiscal_year: int) -> float | None:
    """Return the first non-None annual value for the given metric."""
    tags = XBRL_MAP.get(metric_key, [])
    us_gaap = facts.get("facts", facts).get("us-gaap", {})
    for tag in tags:
        entry = us_gaap.get(tag)
        if not entry:
            continue
        units = entry.get("units", {})
        values = units.get("USD", units.get("pure", units.get("shares", [])))
        # Filter annual 10-K for the target fiscal year
        for v in sorted(values, key=lambda x: x.get("end", ""), reverse=True):
            fy_match = (v.get("fy") == fiscal_year) or (
                str(fiscal_year) in str(v.get("end", ""))
            )
            if (
                v.get("form") in ("10-K", "10-K/A")
                and v.get("val") is not None
                and fy_match
                and v.get("fp") in ("FY", None)
                and len(str(v.get("end", ""))) == 10
            ):
                return float(v["val"])
    return None
