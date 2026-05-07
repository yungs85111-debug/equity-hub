-- Skills_core §13 — DB schema for EQUITY HUB demo
-- 7 tables + 6 indexes

CREATE TABLE IF NOT EXISTS companies (
    ticker         TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    sector         TEXT NOT NULL,
    gics_industry  TEXT,
    cik            TEXT,
    exchange       TEXT
);

CREATE TABLE IF NOT EXISTS financials (
    ticker              TEXT NOT NULL,
    fiscal_year         INTEGER NOT NULL,
    revenue             REAL,
    gross_profit        REAL,
    operating_income    REAL,
    net_income          REAL,
    eps_diluted         REAL,
    total_assets        REAL,
    total_equity        REAL,
    total_debt          REAL,
    cash                REAL,
    inventory           REAL,
    accounts_receivable REAL,
    operating_cashflow  REAL,
    capex               REAL,
    interest_expense    REAL,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

CREATE TABLE IF NOT EXISTS prices (
    ticker            TEXT NOT NULL,
    price_date        TEXT NOT NULL,
    stock_price       REAL,
    market_cap        REAL,
    price_change_pct  REAL,
    price_change_1y   REAL,
    PRIMARY KEY (ticker, price_date),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

CREATE TABLE IF NOT EXISTS metrics (
    ticker         TEXT NOT NULL,
    fiscal_year    INTEGER NOT NULL,
    gpm            REAL,
    opm            REAL,
    npm            REAL,
    roe            REAL,
    roa            REAL,
    rev_yoy        REAL,
    rev_3y_cagr    REAL,
    dr             REAL,
    icr            REAL,
    cr             REAL,
    asset_turn     REAL,
    inv_turn       REAL,
    per            REAL,
    pbr            REAL,
    psr            REAL,
    ev_ebitda      REAL,
    fcf            REAL,
    fcf_margin     REAL,
    div_yield      REAL,
    net_cash       REAL,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

CREATE TABLE IF NOT EXISTS tiers (
    ticker             TEXT NOT NULL,
    fiscal_year        INTEGER NOT NULL,
    tier_profitability TEXT,
    tier_growth        TEXT,
    tier_stability     TEXT,
    tier_efficiency    TEXT,
    tier_valuation     TEXT,
    tier_cash_power    TEXT,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

CREATE TABLE IF NOT EXISTS scores (
    ticker            TEXT NOT NULL,
    fiscal_year       INTEGER NOT NULL,
    common_score      REAL,
    sector_score      REAL,
    total_score       REAL,
    overall_tier      TEXT,
    sector_percentile REAL,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

CREATE TABLE IF NOT EXISTS insights (
    ticker      TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    seq         INTEGER NOT NULL,
    kind        TEXT,
    title       TEXT,
    body        TEXT,
    PRIMARY KEY (ticker, fiscal_year, seq),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

CREATE INDEX IF NOT EXISTS idx_fin_ticker_fy   ON financials(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_met_ticker_fy   ON metrics(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_tier_ticker_fy  ON tiers(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_score_sector    ON scores(fiscal_year, overall_tier);
CREATE INDEX IF NOT EXISTS idx_score_overall   ON scores(overall_tier);
CREATE INDEX IF NOT EXISTS idx_prices_date     ON prices(price_date);
