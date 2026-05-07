"""yfinance price + valuation supplement — Skills_core §10 Step 6."""
import time

try:
    import yfinance as yf
    _YF_AVAILABLE = True
except ImportError:
    _YF_AVAILABLE = False


def get_price_data(ticker: str, retries: int = 3) -> dict:
    """Return {stock_price, market_cap, price_change_pct, price_change_1y, per, pbr, price_date}."""
    if not _YF_AVAILABLE:
        return {}

    for attempt in range(retries):
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period="1y")

            if hist.empty:
                return {}

            current_price = float(hist["Close"].iloc[-1])
            year_ago_price = float(hist["Close"].iloc[0]) if len(hist) > 1 else current_price
            price_change_1y = ((current_price - year_ago_price) / year_ago_price * 100) if year_ago_price else None

            return {
                "stock_price": current_price,
                "market_cap": info.get("marketCap"),
                "price_change_pct": info.get("52WeekChange"),
                "price_change_1y": price_change_1y,
                "per": info.get("trailingPE"),
                "pbr": info.get("priceToBook"),
                "price_date": str(hist.index[-1].date()),
            }
        except Exception:
            if attempt == retries - 1:
                return {}
            time.sleep(2)
    return {}
