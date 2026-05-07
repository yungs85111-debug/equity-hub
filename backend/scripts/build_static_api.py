"""정적 JSON 빌더 — Flask test_client로 모든 API 응답을 frontend/public/data/에 덤프.
Usage: python -m backend.scripts.build_static_api
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

# 프로젝트 루트를 sys.path에 추가 (모듈로 실행되지 않은 경우 대비)
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import app  # noqa: E402
from backend.config import DB_PATH, FISCAL_YEAR  # noqa: E402

OUT_DIR = ROOT / "frontend" / "public" / "data"

# 프론트엔드가 요청하는 모든 indicator 이름 (CompanyDetail의 six_core + kpis)
# six_core 첫 키: opm, rev_yoy, dr, asset_turn, per, fcf_margin
# kpis: rev_yoy, opm, roe, net_cash
# 추가 안전망: 인기 metric들 (popup에서 다른 키로도 접근 가능성 있음)
INDICATOR_KEYS = [
    "opm", "roe", "gpm",
    "rev_yoy", "rev_3y_cagr",
    "dr", "icr",
    "asset_turn", "inv_turn",
    "per", "ev_ebitda", "pbr",
    "fcf_margin", "fcf",
    "net_cash",
]


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _fetch(client, url: str) -> dict | None:
    """test_client로 GET 호출 후 JSON 반환. 비-200은 None."""
    r = client.get(url)
    if r.status_code != 200:
        print(f"  WARN {r.status_code} {url}")
        return None
    return r.get_json()


def main() -> None:
    # 출력 디렉토리 초기화
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    print(f"OUT: {OUT_DIR}")

    # DB에서 sector·ticker 목록 동적 추출 (하드코딩 금지)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    sectors = [r["sector"] for r in conn.execute(
        "SELECT DISTINCT sector FROM companies WHERE sector IS NOT NULL ORDER BY sector"
    ).fetchall()]
    tickers = [r["ticker"] for r in conn.execute(
        "SELECT ticker FROM companies ORDER BY ticker"
    ).fetchall()]
    conn.close()

    print(f"섹터: {len(sectors)}개, 종목: {len(tickers)}개, FY={FISCAL_YEAR}")

    count = 0
    with app.test_client() as client:
        # 1) /api/health
        data = _fetch(client, "/api/health")
        if data is not None:
            _write_json(OUT_DIR / "health.json", data)
            count += 1

        # 2) /api/sectors
        data = _fetch(client, "/api/sectors")
        if data is not None:
            _write_json(OUT_DIR / "sectors.json", data)
            count += 1

        # 3) /api/sector/<name>?tab={understand|compare}
        # 파일명은 raw UTF-8 사용 (정적 서버는 URL을 decode해서 파일을 찾음)
        for sector in sectors:
            url_name = quote(sector, safe="")
            for tab in ("understand", "compare"):
                data = _fetch(client, f"/api/sector/{url_name}?tab={tab}")
                if data is not None:
                    _write_json(OUT_DIR / "sector" / f"{sector}.{tab}.json", data)
                    count += 1

        # 4) /api/company/<ticker>
        for ticker in tickers:
            data = _fetch(client, f"/api/company/{ticker}")
            if data is not None:
                _write_json(OUT_DIR / "company" / f"{ticker}.json", data)
                count += 1

        # 5) /api/indicator/<ticker>/<name>
        for ticker in tickers:
            for ind in INDICATOR_KEYS:
                data = _fetch(client, f"/api/indicator/{ticker}/{ind}")
                if data is not None:
                    _write_json(OUT_DIR / "indicator" / ticker / f"{ind}.json", data)
                    count += 1

    print(f"\nOK {count}개 JSON 파일 생성 완료 → {OUT_DIR}")


if __name__ == "__main__":
    main()
