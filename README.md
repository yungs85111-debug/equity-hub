# EQUITY HUB — 교육용 투자 분석 대시보드

> ⚠️ 교육 목적으로만 제작되었습니다. 투자 추천·매수·매도 의견이 아닙니다.

S&P 500 / NASDAQ 100 기준 190개 종목의 SEC EDGAR 재무 데이터를 6대 코어 스탯(수익성/성장성/안정성/효율성/밸류에이션/현금창출력)으로 변환해 S/A/B/C 티어로 시각화하는 교육용 대시보드입니다.

---

## 빠른 시작

### 요구사항

- Python 3.11+
- Node.js 18+

### 1. 저장소 클론 및 의존성 설치

```bash
# 백엔드
pip install -r backend/requirements.txt

# 프론트엔드
cd frontend && npm install && cd ..
```

### 2. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
# backend/.env 에서 필요 시 값 수정 (기본값으로 demo 실행 가능)
```

### 3. DB 초기화 및 데모 데이터 적재

```bash
# DB 스키마 초기화
python -m backend.db.init_db

# demo_fixture.json → demo.db 적재 (demo.db가 비어 있을 때)
python -c "import sys; sys.path.insert(0,'.'); from backend.services.seed_demo import main; main()"
```

### 4. 서버 실행

```bash
# 터미널 1: Flask 백엔드 (포트 5000)
python run.py

# 터미널 2: Vite 프론트엔드 (포트 5173)
cd frontend && npm run dev
```

브라우저에서 **http://localhost:5173** 접속

---

## 실측 데이터 수집 (선택)

`demo_fixture.json`은 이미 커밋되어 있어 바로 사용 가능합니다.
새로운 실측 데이터를 수집하려면:

```bash
# 약 30~60분 소요 (190 종목 × EDGAR API + yfinance)
python -c "
import sys, os
sys.path.insert(0, '.')
os.environ['DATA_MODE'] = 'live'
from backend.services.fetch_edgar import main
main()
"

# 수집 후 DB 재적재
python -c "import sys; sys.path.insert(0,'.'); from backend.services.seed_demo import main; main()"
```

---

## 환경 변수 (backend/.env)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `DATA_MODE` | `demo` | `demo` = fixture 사용, `live` = EDGAR 실수집 |
| `EDGAR_USER_AGENT` | `EQUITY HUB Demo ...` | EDGAR SEC 규정 필수 헤더 |
| `DB_PATH` | `backend/demo.db` | SQLite DB 경로 (프로젝트 루트 기준) |
| `FISCAL_YEAR` | `2023` | 분석 기준 회계연도 |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS 허용 출처 |

---

## 프로젝트 구조

```
dashboard/
├── run.py                    ← Flask 실행 진입점
├── backend/
│   ├── app.py                ← Flask 앱 팩토리
│   ├── config.py             ← 환경 변수 로드
│   ├── db/                   ← SQLite 스키마 · 연결 · 초기화
│   ├── routes/               ← API 블루프린트 (health/sectors/sector/company/indicator)
│   ├── services/             ← EDGAR 수집 · 지표 계산 · 티어링 · 스코어 · 인사이트
│   └── data/                 ← tickers_165.json · sector_definitions.json · demo_fixture.json
└── frontend/
    ├── src/
    │   ├── pages/            ← SectorHub · SectorStatboard · CompanyDetail · NotFound
    │   ├── components/       ← layout · common · sector · popup
    │   ├── hooks/            ← useApi · useIndicatorPopup
    │   ├── lib/              ← api · format · tier
    │   ├── config/           ← skills_config.ts (색상 상수 단일 소스)
    │   └── types/            ← API 응답 인터페이스
    └── vite.config.ts        ← /api → :5000 프록시
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/health` | 서버 상태 · data_mode · 기준일 |
| GET | `/api/sectors` | 11개 섹터 요약 (티어 분포 포함) |
| GET | `/api/sector/:name?tab=understand\|compare` | 섹터 상세 (6대 스탯 평균 / 히트맵) |
| GET | `/api/company/:ticker` | 기업 상세 (Overall 티어 · 6코어 스탯 · KPI · 인사이트) |
| GET | `/api/indicator/:ticker/:name` | 지표 팝업 (정의 · 백분위수 · 섹터 비교) |

---

## 티어 기준 (Skills_core §4)

| 티어 | 색상 | 총점 기준 |
|---|---|---|
| S | 에메랄드 (#22C55E) | 80점 이상 |
| A | 블루 (#60A5FA) | 65~79점 |
| B | 앰버 (#F59E0B) | 45~64점 |
| C | 레드 (#EF4444) | 44점 이하 |

총점 = 공통점수(40%) × 0.4 + 섹터점수(60%) × 0.6

---

## Vercel 정적 배포

데모 모드는 시간 의존성이 없고 외부 API 호출이 없어 정적 JSON으로 변환 후 Vercel에 배포할 수 있습니다.

### 배포 절차

1. GitHub 저장소를 Vercel에 import (https://vercel.com/new)
2. Framework Preset: **Other** 선택 (vercel.json이 자동 인식)
3. 환경 변수 설정 불필요 (기본값 사용)
4. **Deploy** 클릭

Vercel이 자동으로:
- `pip install -r backend/requirements.txt`
- `python -m backend.db.init_db` (스키마 생성)
- `python -m backend.services.seed_demo` (fixture → DB)
- `python -m backend.services.recompute_tiers` (티어 재계산)
- `cd frontend && npm run build`
  - prebuild 훅: `python ../backend/scripts/build_static_api.py` → 약 3,064개 정적 JSON 생성
  - Vite build → `frontend/dist/`
- `vercel.json` rewrites: `/api/*` → `/data/*.json` 매핑

### 정적 JSON 빌드만 실행

```bash
python -m backend.scripts.build_static_api
# → frontend/public/data/ 아래 JSON 트리 생성 (약 3,064개, 9~10MB)
```

### 새 fixture 후 재배포

```bash
# 1. EDGAR 재수집 (선택)
DATA_MODE=live python -m backend.services.fetch_edgar

# 2. 커밋 & 푸시
git add backend/data/demo_fixture.json
git commit -m "Update fixture: FY{YEAR}"
git push

# 3. Vercel이 자동 재배포
```

---

## 면책 고지

- 본 서비스는 **교육 목적**으로만 제작되었습니다.
- 투자 추천·매수·매도 의견이 아닙니다.
- 전문 투자 도구나 전문가 의견을 대체하지 않습니다.
- 데이터 출처: SEC EDGAR (10-K 연간 보고서), Yahoo Finance (시세)
- Skills_core v4.4.2 / Skills_ui v4.4.1 기준
