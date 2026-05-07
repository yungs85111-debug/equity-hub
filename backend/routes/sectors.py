from flask import Blueprint, jsonify, request
import sqlite3

from backend.config import DB_PATH, FISCAL_YEAR

sectors_bp = Blueprint("sectors", __name__)


@sectors_bp.get("/api/sectors")
def get_sectors():
    fy = request.args.get("fiscal_year", FISCAL_YEAR, type=int)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Get latest price_date
    pd_row = conn.execute("SELECT MAX(price_date) FROM prices").fetchone()
    price_date = pd_row[0] if pd_row else None

    rows = conn.execute("""
        SELECT
            c.sector,
            COUNT(*) AS n,
            AVG(sc.total_score) AS avg_score,
            AVG(sc.common_score) AS avg_common,
            SUM(CASE WHEN sc.overall_tier='S' THEN 1 ELSE 0 END) AS n_s,
            SUM(CASE WHEN sc.overall_tier='A' THEN 1 ELSE 0 END) AS n_a,
            SUM(CASE WHEN sc.overall_tier='B' THEN 1 ELSE 0 END) AS n_b,
            SUM(CASE WHEN sc.overall_tier='C' THEN 1 ELSE 0 END) AS n_c
        FROM companies c
        JOIN scores sc ON c.ticker = sc.ticker AND sc.fiscal_year = ?
        GROUP BY c.sector
    """, (fy,)).fetchall()
    conn.close()

    sectors = []
    for r in rows:
        n = r["n"] or 1
        avg = round(r["avg_score"] or 0, 1)
        avg_common = r["avg_common"] or 0
        n_s, n_a, n_b, n_c = r["n_s"] or 0, r["n_a"] or 0, r["n_b"] or 0, r["n_c"] or 0

        sectors.append({
            "sector":      r["sector"],
            "n":           n,
            "avg_score":   avg,
            "avg_common":  round(avg_common, 1),
            "n_s": n_s, "n_a": n_a, "n_b": n_b, "n_c": n_c,
            "s_pct": round(n_s / n * 100, 1),
            "a_pct": round(n_a / n * 100, 1),
            "b_pct": round(n_b / n * 100, 1),
            "c_pct": round(n_c / n * 100, 1),
            "price_date": price_date,
            "overall_tier": "B",  # placeholder, set below
        })

    # 섹터 간 상대 순위로 등급 결정 (common_score 기준)
    # total_score는 섹터 내 백분위 포함이라 모든 섹터가 동일하게 수렴하므로 사용 불가
    sectors.sort(key=lambda x: x["avg_common"], reverse=True)
    n_sectors = len(sectors)
    for i, s in enumerate(sectors):
        pct_rank = i / max(n_sectors - 1, 1)  # 0(1위) ~ 1(꼴찌)
        if pct_rank <= 0.18:    s["overall_tier"] = "S"
        elif pct_rank <= 0.45:  s["overall_tier"] = "A"
        elif pct_rank <= 0.75:  s["overall_tier"] = "B"
        else:                   s["overall_tier"] = "C"

    # Sort by canonical sector order
    SECTOR_ORDER = ["IT", "금융", "헬스케어", "경기소비재", "필수소비재",
                    "에너지", "산업재", "유틸리티", "소재", "커뮤니케이션", "부동산"]
    sectors.sort(key=lambda x: SECTOR_ORDER.index(x["sector"]) if x["sector"] in SECTOR_ORDER else 99)

    return jsonify({"sectors": sectors, "fiscal_year": fy, "price_date": price_date})
