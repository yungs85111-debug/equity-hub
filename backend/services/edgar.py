"""EDGAR API client — Skills_core §1.
Rate limit: 10 req/s → 100ms sleep between calls.
"""
import time
import requests

from backend.config import EDGAR_USER_AGENT

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": EDGAR_USER_AGENT,
    "Accept": "application/json",
})

_RATE_MS = 0.1  # 100ms between requests


def _get(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            time.sleep(_RATE_MS)
            resp = _SESSION.get(url, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            if attempt == retries - 1:
                raise
            wait = _RATE_MS * (2 ** attempt)
            time.sleep(wait)
    return {}


def get_company_tickers() -> dict:
    """Return {ticker: {cik_str, title, ticker}} mapping."""
    url = "https://www.sec.gov/files/company_tickers.json"
    raw = _get(url)
    return {v["ticker"]: v for v in raw.values()}


def get_companyfacts(cik: str) -> dict:
    """Return companyfacts JSON for given CIK."""
    padded = str(cik).lstrip("0").zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded}.json"
    return _get(url)


def get_submissions(cik: str) -> dict:
    padded = str(cik).lstrip("0").zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{padded}.json"
    return _get(url)
