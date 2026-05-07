# Investment Analysis Skills — Core
# 주식 기본적 분석 게임형 대시보드 — 데이터·계산·DB 규칙

**버전:** 4.4.2-core (v4.4.1 기반 / demo.db 종목 50개 → 165개 확대 — 전 섹터 n≥15 분위수 작동)
**포함 섹션:** §0 역할 · §1 데이터 수집 · §1-bis 데모모드 · §2 코어 스탯 계산 · §3 티어·점수화 · §4 섹터 벤치마크 · §9 다중 형식 · §10 파이프라인 · §13 DB 스키마 · §14 SIC→GICS
**UI 규칙:** Skills_ui.md 참조
**컨셉:** 뇌동매매 하지 말고, 알고 투자하자
**데이터 원천:** SEC EDGAR (data.sec.gov) — API 키 불필요, 무료
**분석 프레임워크:** 6대 코어 스탯 체계 (수익성 / 성장성 / 안정성 / 효율성 / 밸류에이션 / 현금창출력)
**섹터 분류:** GICS 11개 섹터 (SIC → GICS 자동 변환)
**UI 방향:** 게임 스탯 트리 — 섹터 허브 → 기업 비교 → 기업 상세 드릴다운
**상태 표현:** S / A / B / C 티어 + 스테이터스 레이블 병행
**교육 목적:** 복잡한 재무지표를 숫자 나열이 아닌 상태판·속성치·티어·비교 우위로 변환해 누구나 빠르게 해석할 수 있도록 한다.

---

## 0. 이 문서의 역할

이 문서는 **Skills_core.md** 입니다. 데이터 수집·지표 계산·티어 판정·점수화·DB 스키마 규칙을 담습니다.
UI 레이아웃·교육 콘텐츠·인사이트 문장 규칙은 **Skills_ui.md** 를 참조하십시오.

이 문서 한 장을 Claude / Cursor 등 AI 코드 생성 도구에 붙여넣으면
**데이터 수집 → 지표 계산 → 티어 판정 → 점수화 → DB 저장**까지
전 과정을 수동 코딩 없이 자동 생성할 수 있도록 설계되었다.

전체 처리 순서는 **§10 파이프라인 흐름 요약**을 참조한다.

---

## 0-bis. 타깃 사용자 정의

```
타깃 사용자: 투자를 시작한 지 1~3년 차,
             재무제표를 읽고 싶지만 어디서 시작해야 할지 모르는 30~40대.

게임 메타포(S/A/B/C 티어, 캐릭터 시트)는 "어렵게 느껴지는 재무 숫자를
빠르게 파악"하기 위한 시각적 장치다.
투자 전문가용 분석 도구가 아님을 모든 화면에서 명확히 한다.
```

---

## 1-bis. 데모 모드 운영 규칙

### 운영 원칙

```
DATA_MODE = "live" | "demo"   ← 환경변수로 전환

demo 모드 : DB 직접 조회만 수행. EDGAR / yfinance 호출 없음.
            응답 속도 목표: 화면 전환 1초 이내.
live 모드 : §1 파이프라인 전체 동작 (실시간 수집).

demo.db 갱신 주기: 수동 (분기 1회 권장)
기준일 표기 필수: 모든 화면에 "데이터 기준: {price_date}" 명시
```

### 사전 적재 종목 165개 (demo.db 구성)

```
⚠️ 변경 이유 (v4.4.1 → v4.4.2):
   §4.0 분위수 계산 조건: n < 10 → fallback 강제 전환
   기존 50개는 IT(10개)만 경계선, 나머지 10섹터 전부 fallback
   → 165개로 확대, 전 섹터 n ≥ 15 확보

IT (20)       : AAPL, MSFT, NVDA, GOOGL, META, AMZN, TSLA, ORCL, AMD, INTC,
                QCOM, TXN, MU, ADBE, CRM, NOW, SNOW, PLTR, DELL, HPQ
금융 (20)     : JPM, BAC, WFC, GS, MS,
                C, USB, TFC, PNC, COF, AXP, BLK, SCHW, ICE, CME,
                MET, PRU, AFL, ALL, AIG
헬스케어 (20) : JNJ, UNH, PFE, ABBV, MRK,
                BMY, AMGN, GILD, CVS, CI, ELV, HCA, MDT, SYK,
                BSX, ZBH, ISRG, IQV, DGX, MCK
경기소비재 (20): HD, NKE, MCD, SBUX, TGT,
                LOW, TJX, BKNG, MAR, HLT, YUM, DRI, ROST,
                ORLY, AZO, BBY, F, GM, APTV, LVS
필수소비재 (15): PG, KO, PEP, WMT, COST,
                CL, GIS, K, HSY, MKC, CHD, SJM, CAG, TSN, HRL
에너지 (15)   : XOM, CVX, COP,
                EOG, MPC, PSX, VLO, PXD, HAL, SLB, BKR,
                OXY, DVN, FANG, MRO
산업재 (20)   : CAT, BA, HON, UPS, DE,
                GE, MMM, EMR, ETN, ROK, CARR, OTIS, LMT,
                RTX, NOC, GD, WM, RSG, FDX, CSX
유틸리티 (15) : NEE, DUK, SO,
                AES, EXC, PCG, XEL, WEC, ES, ETR, PPL,
                CNP, AEE, CMS, PNW
소재 (15)     : LIN, APD, NEM,
                FCX, NUE, STLD, VMC, MLM, PPG, SHW, ECL,
                IFF, CE, ALB, MOS
커뮤니케이션 (15): DIS, NFLX, T, VZ,
                CMCSA, CHTR, PARA, WBD, EA, TTWO,
                MTCH, ZM, IAC, FOXA, OMC
부동산 (15)   : AMT, PLD, SPG,
                EQIX, PSA, O, WY, ARE, VTR, WELL,
                EQR, AVB, MAA, UDR, CPT

분위수 충족: 전 섹터 n ≥ 15 → §4.0 동적 벤치마크 전 섹터 작동
```

### demo 모드 코드 패턴

```python
import os

DATA_MODE = os.getenv("DATA_MODE", "demo")

def get_metrics(ticker: str, db_conn):
    """demo 모드: DB 직접 조회 / live 모드: EDGAR 수집 후 조회"""
    if DATA_MODE == "demo":
        return db_conn.execute(
            "SELECT * FROM metrics WHERE ticker=? ORDER BY fiscal_year DESC LIMIT 1",
            (ticker,)
        ).fetchone()
    else:
        fetch_and_store(ticker, db_conn)   # §1 파이프라인 호출
        return db_conn.execute(
            "SELECT * FROM metrics WHERE ticker=? ORDER BY fiscal_year DESC LIMIT 1",
            (ticker,)
        ).fetchone()
```

### 주가 데이터 처리 (yfinance 의존 제거)

```python
# yfinance는 수집 시점에 한 번만 호출해 prices 테이블에 저장한다.
# 심사/데모 중 재호출 없음.
# UI에 "주가 기준일: {price_date}" 명시 → 데이터 투명성 확보

# Fallback 우선순위:
# 1. prices 테이블 저장값 사용
# 2. 없으면 → stock_price = null, 밸류에이션 티어 UNKNOWN 표시
# 3. yfinance 재시도는 live 모드에서만 수행 (최대 3회, 간격 2초)
```

---

## 1. 데이터 수집 규칙 (SEC EDGAR API)

### 1.1 API 개요

```
베이스 URL : https://data.sec.gov
인증       : 없음 (API 키 불필요)
필수 헤더  : User-Agent: <앱이름> <연락처이메일>
Rate Limit : 초당 10 요청 — 요청 간 100ms 이상 대기 필수
포맷       : JSON
```

**User-Agent 기본값 규칙:**

코드 생성 시, 사용자가 별도로 User-Agent 값을 제공하지 않은 경우
아래 기본 문자열을 하드코딩하여 사용한다.
실제 배포 시에는 반드시 앱 이름과 연락처 이메일로 변경해야 한다.

```python
# ⚠️ 실제 배포 시 아래 값을 본인의 앱 이름과 이메일로 변경하세요.
# SEC EDGAR는 User-Agent 미설정 시 요청을 차단할 수 있습니다.
DEFAULT_USER_AGENT = "MyEdgarDashboard (your_email@example.com)"

headers = {
    "User-Agent": DEFAULT_USER_AGENT
}
```

### 1.2 엔드포인트 3종

```
# ① ticker → CIK 변환 (최초 1회 다운로드 후 로컬 캐시)
GET https://www.sec.gov/files/company_tickers.json

# ② 회사 기본 정보 + 공시 이력
GET https://data.sec.gov/submissions/CIK{10자리}.json

# ③ 전체 XBRL 재무 데이터 (이 하나로 전 기간 손익·재무·현금흐름 확보)
GET https://data.sec.gov/api/xbrl/companyfacts/CIK{10자리}.json
```

**companyfacts 응답 구조:**
```json
{
  "facts": {
    "us-gaap": {
      "Revenues": {
        "units": {
          "USD": [
            { "end": "2023-09-30", "val": 383285000000,
              "form": "10-K", "accn": "...", "fy": 2023, "fp": "FY" }
          ]
        }
      }
    }
  }
}
```

### 1.3 수집 원천 데이터 항목

#### 기업 메타데이터
```
종목명, 티커, 거래소, 국가
GICS Sector / Industry Group / Industry / Sub-Industry 코드 및 명칭
시가총액, 상장주식수
```

#### 손익계산서
```
매출액 (revenue)
매출총이익 (gross_profit)
영업이익 (operating_income)
EBITDA (ebitda = operating_income + depreciation)
순이익 (net_income)
EPS 희석 (eps_diluted)
```

#### 재무상태표
```
총자산 (total_assets)
자기자본 (total_equity)
유동자산 (current_assets)
유동부채 (current_liabilities)
현금 및 현금성자산 (cash)
금융부채 (total_debt = 단기차입금 + 장기차입금)  ← 안정성 지표·부채비율 계산에 사용
재고자산 (inventory)                              ← 효율성 지표(재고자산회전율) 계산에 사용
매출채권 (accounts_receivable)                    ← 효율성 지표(매출채권회전율) 계산에 사용

⚠️ DR(부채비율) = total_debt / total_equity
   회계상 총부채(total_assets - total_equity)는 별도 컬럼으로 저장하지 않는다.
   AI 코드 생성 시 book_liabilities 변수명 사용 금지 — total_debt 사용 강제.
```

#### 현금흐름표
```
영업현금흐름 (operating_cashflow)
자본적지출 (capex)
잉여현금흐름 (fcf = operating_cashflow - capex)
```

#### 시장 데이터 (yfinance 보완)
```
설치: pip install yfinance
주가 (stock_price)
시가총액 (market_cap)
배당금 / 배당수익률 (dividends_per_share, dividend_yield)

⚠️ yfinance는 비공식 API로 응답 구조가 변경될 수 있다.
   Fallback 처리 규칙:
   - yfinance 호출 실패(예외 발생) → stock_price / market_cap = null
   - null 시 밸류에이션 스탯 전체 티어 UNKNOWN 처리
   - 재시도: 최대 3회, 간격 2초
```

### 1.4 XBRL 태그 매핑 테이블

> 같은 지표라도 회사마다 태그가 다르다. 우선순위 순서로 시도하고, 모두 없으면 `null` 처리한다.

| 표준 필드 | 시도 순서 (XBRL 태그) |
|----------|----------------------|
| `revenue` | `Revenues` → `RevenueFromContractWithCustomerExcludingAssessedTax` → `SalesRevenueNet` |
| `gross_profit` | `GrossProfit` |
| `operating_income` | `OperatingIncomeLoss` |
| `net_income` | `NetIncomeLoss` → `ProfitLoss` → `NetIncome` |
| `total_assets` | `Assets` |
| `total_equity` | `StockholdersEquity` → `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` |
| `total_debt` | `LongTermDebt` + `ShortTermBorrowings` → `DebtCurrent` + `LongTermDebtNoncurrent` |
| `current_assets` | `AssetsCurrent` |
| `current_liabilities` | `LiabilitiesCurrent` |
| `cash` | `CashAndCashEquivalentsAtCarryingValue` → `Cash` |
| `operating_cashflow` | `NetCashProvidedByUsedInOperatingActivities` |
| `capex` | `PaymentsToAcquirePropertyPlantAndEquipment` |
| `interest_expense` | `InterestExpense` → `InterestAndDebtExpense` |
| `depreciation` | `DepreciationDepletionAndAmortization` → `Depreciation` |
| `shares_outstanding` | `CommonStockSharesOutstanding` (instant, 기간 말 기준) |
| `dividends_per_share` | `CommonStockDividendsPerShareDeclared` → `CommonStockDividendsPerShareCashPaid` |
| `eps_diluted` | `EarningsPerShareDiluted` |
| `inventory` | `InventoryNet` → `Inventories` |
| `accounts_receivable` | `AccountsReceivableNetCurrent` → `ReceivablesNetCurrent` |

> ⚠️ **`inventory` null 처리:** 금융·유틸리티·부동산·소프트웨어 기업은 재고가 없어 null이 정상.
>   null인 경우 재고자산회전율 = null, 티어 = UNKNOWN 처리 (오류 아님).
> ⚠️ **`accounts_receivable` null 처리:** 선불 매출(구독형) 기업은 매출채권이 0 또는 null일 수 있음.
>   0이면 매출채권회전율 = null, UNKNOWN 처리 (ZeroDivisionError 방지).

### 1.5 연간 데이터 추출 규칙

```
조건 1: form = "10-K"  (연간 보고서만)
조건 2: fp   = "FY"    (전체 회계연도)
조건 3: 중복 제거 — 동일 fy + 동일 태그가 여러 개면 accn(접수번호) 최신 것 선택
조건 4: 기간 순 정렬 — end 날짜 오름차순
조건 5: 최소 3개년 / 최대 5개년 수집 (성장성·추세 계산용)
재무상태표: fp="FY" AND form="10-K" → end 날짜 기준 회계연도 말 값 사용
```

### 1.6 결측값 처리

| 상황 | 처리 |
|------|------|
| 단일 태그 결측 | 대체 태그 시도 → 모두 없으면 `null`, 티어 `UNKNOWN` |
| 연간 데이터 1개년만 존재 | 성장성 계산 생략, `NO HISTORY` |
| `operating_income = null` | `ebitda` 계산 생략 → `null`, EV/EBITDA 티어 `UNKNOWN` |
| `total_equity < 0` | 안정성 스탯 강제 `IMPAIRED` |
| `interest_expense = 0` | ICR 표시 `DEBT-FREE` |
| `FCF < 0` | 음수 그대로 표시; 섹터 분위수 계산에 포함 → 자동 하위 분위 → C티어 |
| 코어 스탯 3개 이상 null | 대시보드 상단 배너: `DATA INSUFFICIENT` |

---

## 2. 6대 코어 스탯 계산 규칙

> 지표를 절대값으로 나열하지 않는다.
> 6개 축의 스탯으로 변환해 게임 캐릭터 시트처럼 읽는다.

### 스탯 1 — 수익성 (Profitability)
> "이 기업은 장사를 잘 하는가?"

| 지표 | 계산식 | 단위 |
|------|--------|------|
| 매출총이익률 (GPM) | `gross_profit / revenue × 100` | % |
| 영업이익률 (OPM) | `operating_income / revenue × 100` | % |
| 순이익률 (NPM) | `net_income / revenue × 100` | % |
| ROE | `net_income / total_equity × 100` | % |
| ROA | `net_income / total_assets × 100` | % |
| (선택) ROIC | `operating_income × (1-세율) / 투하자본 × 100` | % |

### 스탯 2 — 성장성 (Growth)
> "이 기업은 커지고 있는가?"

| 지표 | 계산식 | 최소 데이터 |
|------|--------|------------|
| 매출 YoY | `(rev_t / rev_t-1 - 1) × 100` | 2개년 |
| 영업이익 YoY | `(op_t / |op_t-1| - 1) × 100` | 2개년 |
| 순이익 YoY | `(ni_t / |ni_t-1| - 1) × 100` | 2개년 |
| EPS YoY | `(eps_t / |eps_t-1| - 1) × 100` | 2개년 |
| 매출 3Y CAGR | `((rev_t / rev_t-3)^(1/3) - 1) × 100` | 4개년 |
| OPM 변화 | `OPM_t - OPM_t-1` | 2개년 (포인트) |

전년 영업이익 음수 처리: `op_t-1 < 0` → YoY 대신 "흑자 전환" 레이블

### 스탯 3 — 안정성 (Stability)
> "이 기업은 무너지지 않는가?"

| 지표 | 계산식 | 단위 |
|------|--------|------|
| 부채비율 (DR) | `total_debt / total_equity × 100` | % |
| 총부채/총자산 | `(total_assets - total_equity) / total_assets × 100` | % |
| 유동비율 (CR) | `current_assets / current_liabilities × 100` | % |
| 이자보상배율 (ICR) | `operating_income / interest_expense` | 배 |
| (선택) 순차입금/EBITDA | `(total_debt - cash) / ebitda` | 배 |

### 스탯 4 — 효율성 (Efficiency)
> "이 기업은 가진 것을 잘 굴리는가?"

| 지표 | 계산식 | 단위 |
|------|--------|------|
| 총자산회전율 | `revenue / total_assets` | 회 |
| 재고자산회전율 | `revenue / inventory` | 회 |
| 매출채권회전율 | `revenue / accounts_receivable` | 회 |
| 운전자본회전율 | `revenue / (current_assets - current_liabilities)` | 회 |

> 금융·유틸리티·부동산은 효율성 스탯 가중치를 낮게 적용한다 (섹션 4 참조).

### 스탯 5 — 밸류에이션 (Valuation)
> "이 기업의 주가는 적정한가?"

| 지표 | 계산식 | 단위 |
|------|--------|------|
| PER | `stock_price / eps_diluted` | 배 |
| PBR | `stock_price / (total_equity / shares_outstanding)` | 배 |
| PSR | `stock_price / (revenue / shares_outstanding)` | 배 |
| EV/EBITDA | `(market_cap + total_debt - cash) / ebitda` | 배 |
| PEG | `PER / eps_yoy` | 배 |
| (선택) FCF Yield | `fcf / market_cap × 100` | % |

### 스탯 6 — 현금창출력 (Cash Power)
> "이 기업은 실제로 돈을 버는가?"

| 지표 | 계산식 | 단위 |
|------|--------|------|
| OCF | `operating_cashflow` | USD |
| FCF | `operating_cashflow - capex` | USD |
| FCF Margin | `fcf / revenue × 100` | % |
| OCF/순이익 | `operating_cashflow / net_income` | 배 |
| FCF 추세 | 3개년 방향 판정 (개선/유지/악화) | — |
| (선택) 주주환원율 | `(배당+자사주매입) / fcf × 100` | % |

---

## 3. 티어 시스템 및 점수화

### 3.1 티어 정의

> 신호등이나 단순 색상 대신, 게임 등급처럼 읽힌다.
> 모든 티어는 GICS 섹터 기준 상대평가로 결정된다.

| 티어 | 의미 | 섹터 분위 기준 |
|------|------|--------------|
| `S` | 섹터 최상위 — 압도적 강점 | 상위 10% 이상 |
| `A` | 섹터 상위권 — 확실한 강점 | 상위 10~35% |
| `B` | 섹터 평균 — 무난한 수준 | 중간 35~65% |
| `C` | 섹터 하위권 — 약점 존재 | 하위 35% 미만 |
| `IMPAIRED` | 구조적 문제 — 자본잠식·연속 적자 | — |
| `DEBT-FREE` | 무부채 | interest_expense = 0 |
| `UNKNOWN` | 데이터 없음 | null |

> 티어 색상은 **Skills_ui.md §12 컬러 시스템** 참조.
> `DEBT-FREE`는 의도적으로 A티어와 동일 색상(`#60A5FA`) 적용 — 무부채를 긍정 신호로 표현.

DR(부채비율)·총부채/총자산은 반전 적용: **낮을수록 티어 높음.**

### 3.2 스탯별 대표 티어 산출

각 코어 스탯의 대표 티어는 해당 스탯 내 지표들의 티어를 아래 방식으로 집계한다.

```python
def stat_tier(tier_list: list[str]) -> str:
    """
    스탯 내 지표 티어 목록을 받아 대표 티어를 반환한다.
    IMPAIRED가 하나라도 있으면 즉시 IMPAIRED.
    나머지는 최빈값, 동률이면 낮은 티어 우선.
    ※ tier_order.index(t) 양수값 → 인덱스가 클수록(낮은 티어) 우선 선택
    """
    if "IMPAIRED" in tier_list:
        return "IMPAIRED"
    tier_order = ["S", "A", "B", "C", "UNKNOWN"]
    counts = {t: tier_list.count(t) for t in tier_order}
    return max(counts, key=lambda t: (counts[t], tier_order.index(t)))
```

### 3.3 총 투자 점수 산출

> 절대값만으로 점수를 매기면 섹터 간 구조적 차이가 왜곡된다.
> **공통 점수 40% + 섹터 점수 60%** 방식으로 균형을 잡는다.

#### 공통 점수 (0~100점, 40% 반영)

```python
TIER_SCORE = {"S": 100, "A": 75, "B": 50, "C": 25,
              "IMPAIRED": 0, "DEBT-FREE": 75, "UNKNOWN": None}

STAT_WEIGHT_COMMON = {
    "profitability": 0.25,
    "growth":        0.20,
    "stability":     0.20,
    "efficiency":    0.10,
    "valuation":     0.15,
    "cash_power":    0.10,
}

def common_score(stat_tiers: dict) -> float:
    total, weight_sum = 0, 0
    for stat, weight in STAT_WEIGHT_COMMON.items():
        score = TIER_SCORE.get(stat_tiers.get(stat), None)
        if score is not None:
            total += score * weight
            weight_sum += weight
    return round(total / weight_sum, 1) if weight_sum > 0 else None
```

#### 섹터 점수 (0~100점, 60% 반영)

동일 GICS 섹터 내 분위수 기준으로 재산정한다.

```python
def sector_score(ticker: str, sector: str, fiscal_year: int, db_conn) -> float:
    """
    섹터 내 전체 종목의 common_score 분포에서 해당 종목의 백분위를 반환.
    백분위 × 100 = 섹터 점수 (0~100)
    ※ sector 컬럼은 companies 테이블에만 존재 — JOIN 필수

    ⚠️ fetchone() 결과가 None인 경우(미계산 종목) 즉시 None 반환.
       fetchone()[0] 직접 접근 금지 — TypeError 발생.
    """
    scores = db_conn.execute("""
        SELECT sc.common_score
        FROM scores sc
        JOIN companies c ON sc.ticker = c.ticker
        WHERE c.sector = ? AND sc.fiscal_year = ? AND sc.common_score IS NOT NULL
    """, (sector, fiscal_year)).fetchall()
    scores = sorted([r[0] for r in scores])

    row = db_conn.execute("""
        SELECT common_score FROM scores WHERE ticker = ? AND fiscal_year = ?
    """, (ticker, fiscal_year)).fetchone()

    if row is None or row[0] is None:
        return None
    my_score = row[0]

    if not scores:
        return None
    rank = sum(1 for s in scores if s <= my_score)
    return round(rank / len(scores) * 100, 1)
```

#### 최종 총 투자 점수

```python
def total_score(common: float, sector: float) -> float:
    if common is None or sector is None:
        return None
    return round(common * 0.4 + sector * 0.6, 1)
```

#### 총점 → Overall 티어 변환

| 총점 | Overall 티어 |
|------|-------------|
| 85점 이상 | `S` |
| 70~84점 | `A` |
| 50~69점 | `B` |
| 50점 미만 | `C` |
| IMPAIRED 포함 | `IMPAIRED` |

---

## 4. GICS 섹터 벤치마크

> 같은 PER 20배도 IT는 B티어, 금융은 C티어다.
> 아래 정상 범위는 티어 B(섹터 중앙값 구간) 기준이다.
> S티어 = 상단 초과, A티어 = 상단 근방, B티어 = 정상 범위, C티어 = 하단 미달.
>
> ⚠️ **티어 판정 우선순위**
> 1순위: DB에 동일 GICS 섹터 종목이 5개 이상 존재하면 **섹터 내 실측 분위수** 기준으로 판정한다.
> 2순위: 섹터 종목이 5개 미만이거나 DB가 비어 있으면 아래 **절대값 정상 범위**를 fallback으로 사용한다.
> → 절대값 범위는 참고 기준이며 실제 운영 시에는 분위수 판정이 항상 우선한다.

### 4.0 동적 벤치마크 계산 (분위수 자동 산출)

> **하드코딩된 임계값의 출처 불명 문제를 해결한다.**
> demo.db 내 실제 데이터에서 분위수를 계산하고, 출처를 화면에 명시한다.

```python
import numpy as np

def calc_benchmark(db_conn, sector: str, indicator: str, fiscal_year: int) -> dict:
    """
    DB 실측값에서 섹터 벤치마크를 동적으로 계산한다.
    하드코딩 임계값 대신 이 함수의 결과를 티어 판정에 사용한다.

    ⚠️ statistics.quantiles(n=100) 미사용 이유:
       - 반환값이 99개(경계 제외)라 qs[89] 등 인덱스 접근 시 샘플 수에 따라 IndexError 발생
       - numpy.percentile은 임의 샘플 수에서 안전하게 백분위 보간 계산
    최소 샘플 기준: n < 10 → fallback (분위수 신뢰도 확보)
    """
    rows = db_conn.execute(f"""
        SELECT m.{indicator}
        FROM metrics m
        JOIN companies c ON m.ticker = c.ticker
        WHERE c.sector = ?
          AND m.fiscal_year = ?
          AND m.{indicator} IS NOT NULL
    """, (sector, fiscal_year)).fetchall()

    vals = [r[0] for r in rows]
    n = len(vals)

    if n < 10:
        return {"source": "fallback", "n": n}   # 절대값 fallback으로 전환

    qs = np.percentile(vals, [10, 25, 50, 75, 90])
    return {
        "p10":  round(float(qs[0]), 2),
        "p25":  round(float(qs[1]), 2),
        "p50":  round(float(qs[2]), 2),   # 중앙값 = B티어 기준
        "p75":  round(float(qs[3]), 2),
        "p90":  round(float(qs[4]), 2),
        "n":    n,
        "fiscal_year": fiscal_year,
        "source": f"demo.db 실측 {n}개사 ({fiscal_year}년 10-K 기준)"
        # ↑ 이 문자열을 UI에 그대로 노출 → 심사위원 신뢰도 확보
    }

def get_tier_by_percentile(value: float, benchmark: dict,
                            higher_is_better: bool = True) -> str:
    """
    분위수 기반 티어 판정. DR 등 낮을수록 좋은 지표는 higher_is_better=False.
    """
    if benchmark.get("source") == "fallback":
        return None   # 절대값 로직으로 위임

    p10, p25, p75, p90 = (benchmark["p10"], benchmark["p25"],
                           benchmark["p75"], benchmark["p90"])

    if higher_is_better:
        if value >= p90: return "S"
        if value >= p75: return "A"
        if value >= p25: return "B"
        return "C"
    else:   # 낮을수록 좋음 (DR, PER 등 섹터에 따라)
        if value <= p10: return "S"
        if value <= p25: return "A"
        if value <= p75: return "B"
        return "C"
```

**UI 표시 규칙 (벤치마크 출처 명시):**
```
섹터 정상 범위 표시 시 반드시 source 문자열을 함께 표시한다.
예시: "섹터 중앙값 {p50}% (demo.db 실측 5개사, 2023년 10-K 기준)"
⚠️ fallback 사용 시: "섹터 데이터 부족 — S&P 500 평균 기준 적용"
```

### 4.1 절대값 정상 범위 (Fallback — 섹터 종목 5개 미만 시에만 사용)

> ⚠️ 이 테이블은 **fallback 전용**이다.
> DB에 섹터 종목이 5개 이상이면 §4.0 동적 분위수 계산이 항상 우선 적용된다.
> UI에 fallback 사용 사실을 반드시 표시한다.

| 섹터 | OPM | ROE | DR | PER | 우선 강조 지표 |
|------|-----|-----|----|-----|--------------|
| IT | 15~30% | 15~25% | ~100% | 20~40배 | ROE, FCF Margin, 매출 성장 |
| 금융 | 20~35% | 8~15% | ~1000% | 8~12배 | ROE, PBR, 건전성 대체지표 |
| 헬스케어 | 10~25% | 10~20% | ~80% | 25~50배 | 매출 CAGR, FCF, 마진 |
| 경기소비재 | 5~15% | 10~20% | ~150% | 15~25배 | 매출 성장, 재고회전, OPM |
| 필수소비재 | 5~15% | 10~20% | ~150% | 15~25배 | 안정 마진, FCF, 배당성향 |
| 에너지 | 8~20% | 8~18% | ~150% | 10~20배 | EV/EBITDA, FCF, DR |
| 산업재 | 5~15% | 8~15% | ~150% | 12~20배 | OPM, 자산회전, 매출 성장 |
| 유틸리티 | 15~25% | 8~12% | ~300% | 12~18배 | 배당수익률, ICR, 안정 현금흐름 |
| 소재 | 5~15% | 8~15% | ~120% | 10~18배 | OPM, ROIC, 재고회전 |
| 커뮤니케이션 | 15~30% | 10~20% | ~120% | 15~30배 | 성장성, FCF Margin, 수익화 효율 |
| 부동산 | 30~50% | 5~10% | ~300% | N/A | 배당수익률, FFO/AFFO, 레버리지 |

### 4.2 섹터별 스탯 가중치 보정

> 섹터 특성에 따라 6개 스탯의 가중치를 달리 적용한다.

```python
STAT_WEIGHT_SECTOR = {
    "IT":          {"profitability":0.25, "growth":0.25, "stability":0.15,
                    "efficiency":0.05, "valuation":0.15, "cash_power":0.15},
    "금융":        {"profitability":0.30, "growth":0.15, "stability":0.30,
                    "efficiency":0.05, "valuation":0.15, "cash_power":0.05},
    "헬스케어":    {"profitability":0.20, "growth":0.30, "stability":0.15,
                    "efficiency":0.05, "valuation":0.15, "cash_power":0.15},
    "경기소비재":  {"profitability":0.20, "growth":0.25, "stability":0.15,
                    "efficiency":0.15, "valuation":0.15, "cash_power":0.10},
    "필수소비재":  {"profitability":0.25, "growth":0.10, "stability":0.20,
                    "efficiency":0.10, "valuation":0.15, "cash_power":0.20},
    "에너지":      {"profitability":0.20, "growth":0.10, "stability":0.20,
                    "efficiency":0.10, "valuation":0.15, "cash_power":0.25},
    "산업재":      {"profitability":0.20, "growth":0.20, "stability":0.20,
                    "efficiency":0.15, "valuation":0.15, "cash_power":0.10},
    "유틸리티":    {"profitability":0.15, "growth":0.05, "stability":0.25,
                    "efficiency":0.05, "valuation":0.20, "cash_power":0.30},
    "소재":        {"profitability":0.20, "growth":0.15, "stability":0.20,
                    "efficiency":0.20, "valuation":0.15, "cash_power":0.10},
    "커뮤니케이션":{"profitability":0.20, "growth":0.25, "stability":0.15,
                    "efficiency":0.05, "valuation":0.20, "cash_power":0.15},
    "부동산":      {"profitability":0.20, "growth":0.10, "stability":0.25,
                    "efficiency":0.05, "valuation":0.25, "cash_power":0.15},
}
```

---


## 9. 다중 형식 대응 규칙

### 9.1 입력 형식 자동 감지

```
1순위: JSON (EDGAR companyfacts 포맷) → 직접 파싱
2순위: JSON (표준 스키마)              → 직접 파싱
3순위: CSV                            → 헤더 자동 매핑
4순위: 텍스트 표                       → 파싱 후 JSON 변환
```

### 9.2 표준 입력 스키마 (비-EDGAR 데이터 호환)

```json
{
  "ticker":              "AAPL",
  "name":                "Apple Inc.",
  "sector":              "IT",
  "market":              "US",
  "currency":            "USD",
  "fiscal_year":         2023,
  "revenue":             383285,
  "gross_profit":        169148,
  "operating_income":    114301,
  "net_income":           99803,
  "total_assets":        352583,
  "total_equity":         62146,
  "total_debt":          109280,
  "current_assets":      143566,
  "current_liabilities": 145308,
  "cash":                 29965,
  "operating_cashflow":  113736,
  "capex":                10959,
  "interest_expense":      3933,
  "depreciation":         11519,
  "shares_outstanding":   15552,
  "stock_price":          189.30,
  "market_cap":         2941000,
  "dividends_per_share":    0.94
  // ⚠️ 단위: USD 백만달러. 지표 계산 시 × 1,000,000 변환 필수
}
```

### 9.3 한국 시장 확장 시 추가 규칙

```
데이터 원천 : OpenDART (dart.fss.or.kr) + WICS 섹터 매핑
단위        : 억원 → 원 변환 (× 1e8)
섹터 체계   : WICS (GICS 유사, wiseindex.com 크롤링)
주가        : FinanceDataReader (KRX 소스 지정)

⚠️ 벤치마크 기준:
   - 섹션 4의 절대값 범위는 S&P 500 기준이므로 한국 시장에 직접 적용 불가.
   - 한국 확장 시 섹션 4 절대값 fallback 비활성화.
   - DB에 코스피/코스닥 종목이 10개 이상 누적된 후 섹터 분위수 판정만 사용.
   - 분위수 누적 전(초기): 티어 판정 생략, 대시보드에 "데이터 누적 중" 배너 표시.
```

---

## 10. 파이프라인 흐름 요약

```
[Step 1]  ticker 입력 또는 섹터 선택
    ↓
[Step 2]  company_tickers.json에서 CIK 조회
    ↓
[Step 3]  companyfacts/{CIK}.json 1회 호출 (전 기간 확보)
    ↓
[Step 4]  XBRL 태그 매핑 → 표준 필드 추출 (우선순위, 결측 처리)
    ↓
[Step 5]  연간 필터 (form=10-K, fp=FY) + 중복 제거 + 정렬
    ↓
[Step 6]  yfinance로 주가 + 시가총액 보완
    ↓
[Step 7]  6대 코어 스탯 지표 계산
          ├─ fcf = operating_cashflow - capex  (financials → metrics 저장 전 반드시 계산)
          ├─ 재고자산회전율: inventory = null → UNKNOWN (ZeroDivisionError 방지)
          ├─ 매출채권회전율: accounts_receivable = 0 → UNKNOWN
          └─ STAT_WEIGHT_SECTOR(§4.2) 적용 시점:
               common_score(§3.3)는 STAT_WEIGHT_COMMON 사용 (섹터 무관 절대 점수)
               sector_score(§3.3)는 섹터 내 분위수만 사용 (가중치 불필요)
               ※ STAT_WEIGHT_SECTOR는 향후 "섹터 맞춤 공통 점수" 기능 확장용 예약.
                  현재 버전에서는 UI §5.3 섹터 스탯 보드의 강조 지표 선택(§6.2)에만 참고.
    ↓
[Step 8]  GICS 섹터 벤치마크 대비 지표별 티어 판정
    ↓
[Step 9]  스탯별 대표 티어 집계
    ↓
[Step 10] 공통 점수 + 섹터 점수 → 총 투자 점수 + Overall 티어
    ↓
[Step 11] 인사이트 문장 + 지표 팝업 텍스트 자동 생성
    ↓
[Step 12] SQLite 저장 + JSON export
    ↓
[Step 13] 대시보드 자동 렌더링
          ├─ 홈: 섹터 허브 (11개 섹터 카드)
          ├─ 섹터 스탯 보드: 탭1 섹터이해하기 / 탭2 종목비교
          └─ 기업 상세: 캐릭터 시트 (6대 코어 스탯 트리)
```

---


## 13. SQLite 데이터베이스 스키마

```sql
-- Table 1: companies
CREATE TABLE IF NOT EXISTS companies (
    ticker       TEXT PRIMARY KEY,
    cik          TEXT NOT NULL,
    name         TEXT,
    sic_code     TEXT,
    sector       TEXT,           -- GICS 섹터명
    gics_code    TEXT,           -- GICS 8자리 코드 (향후 확장용)
    exchange     TEXT,
    currency     TEXT DEFAULT 'USD',
    updated_at   TEXT DEFAULT (datetime('now'))
);

-- Table 2: financials (연간 재무 원본)
CREATE TABLE IF NOT EXISTS financials (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker               TEXT NOT NULL,
    fiscal_year          INTEGER NOT NULL,
    period_end           TEXT,
    revenue              REAL,
    gross_profit         REAL,
    operating_income     REAL,
    net_income           REAL,
    interest_expense     REAL,
    depreciation         REAL,
    ebitda               REAL,
    eps_diluted          REAL,
    dividends_per_share  REAL,
    total_assets         REAL,
    total_equity         REAL,
    total_debt           REAL,
    current_assets       REAL,
    current_liabilities  REAL,
    cash                 REAL,
    operating_cashflow   REAL,
    capex                REAL,
    inventory            REAL,           -- 재고자산회전율 계산용 (없으면 null 정상)
    accounts_receivable  REAL,           -- 매출채권회전율 계산용 (0이면 UNKNOWN 처리)
    shares_outstanding   REAL,
    created_at           TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Table 3: prices (주가 + 시가총액)
CREATE TABLE IF NOT EXISTS prices (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker           TEXT NOT NULL,
    price_date       TEXT NOT NULL,
    stock_price      REAL NOT NULL,
    market_cap       REAL,
    price_change_pct REAL,           -- 전일 대비 등락률 (오늘의 종목 선정용)
    source           TEXT DEFAULT 'yfinance',
    created_at       TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, price_date),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Table 4: metrics (계산된 지표 — 6대 코어 스탯)
CREATE TABLE IF NOT EXISTS metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    fiscal_year     INTEGER NOT NULL,
    -- 수익성
    gpm             REAL,  opm REAL,  npm REAL,  roe REAL,  roa REAL,
    -- 성장성
    rev_yoy         REAL,  op_yoy REAL,  ni_yoy REAL,  eps_yoy REAL,
    rev_3y_cagr     REAL,  opm_change REAL,
    -- 안정성
    dr              REAL,  debt_to_assets REAL,  cr REAL,  icr REAL,
    net_debt_ebitda REAL,
    -- 효율성
    asset_turnover  REAL,  inventory_turnover REAL,
    receivables_turnover REAL,  working_capital_turnover REAL,
    -- 밸류에이션
    per REAL,  pbr REAL,  psr REAL,  ev_ebitda REAL,  peg REAL,
    fcf_yield REAL,  dividend_yield REAL,
    -- 현금창출력
    ocf REAL,  fcf REAL,  fcf_margin REAL,  ocf_to_ni REAL,
    fcf_trend       TEXT,   -- "개선" / "유지" / "악화"
    price_date      TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Table 5: tiers (티어 판정 결과)
CREATE TABLE IF NOT EXISTS tiers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    fiscal_year     INTEGER NOT NULL,
    -- 스탯별 대표 티어
    tier_profitability  TEXT,
    tier_growth         TEXT,
    tier_stability      TEXT,
    tier_efficiency     TEXT,
    tier_valuation      TEXT,           -- ⚠️ pick_today_stock 쿼리에서 참조 필수
    tier_cash_power     TEXT,
    -- 개별 지표 티어
    tier_opm TEXT, tier_roe TEXT, tier_roa TEXT,
    tier_rev_yoy TEXT, tier_rev_3y_cagr TEXT,
    tier_dr TEXT, tier_cr TEXT, tier_icr TEXT,
    tier_per TEXT, tier_pbr TEXT, tier_ev_ebitda TEXT,
    tier_fcf_margin TEXT, tier_ocf_to_ni TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Table 6: scores (점수화 결과)
CREATE TABLE IF NOT EXISTS scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    fiscal_year     INTEGER NOT NULL,
    common_score    REAL,   -- 공통 점수 (0~100)
    sector_score    REAL,   -- 섹터 점수 (0~100, 분위수 기준)
    total_score     REAL,   -- 최종 총점 (공통 40% + 섹터 60%)
    overall_tier    TEXT,   -- S / A / B / C / IMPAIRED
    sector_percentile REAL, -- 섹터 내 백분위
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Table 7: insights
CREATE TABLE IF NOT EXISTS insights (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker      TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    stat        TEXT NOT NULL,    -- "profitability" / "growth" 등
    indicator   TEXT,
    tier        TEXT,
    message     TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_fin_ticker_fy   ON financials(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_met_ticker_fy   ON metrics(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_tier_ticker_fy  ON tiers(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_score_sector    ON scores(ticker, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_score_overall   ON scores(overall_tier);
CREATE INDEX IF NOT EXISTS idx_prices_date     ON prices(ticker, price_date);
```

---

## 14. SIC → GICS 매핑 (인라인)

```python
SIC_TO_GICS = {
    # IT
    "3570":"IT","3571":"IT","3572":"IT","3575":"IT","3576":"IT",
    "3577":"IT","3578":"IT","3579":"IT","3669":"IT","3672":"IT",
    "3674":"IT","3677":"IT","3678":"IT","3679":"IT","3812":"IT",
    "7370":"IT","7371":"IT","7372":"IT","7373":"IT","7374":"IT",
    "7375":"IT","7376":"IT","7377":"IT","7378":"IT","7379":"IT",
    "3825":"IT","3827":"IT","3829":"IT",
    # 커뮤니케이션
    "4800":"커뮤니케이션","4811":"커뮤니케이션","4812":"커뮤니케이션",
    "4813":"커뮤니케이션","4833":"커뮤니케이션","4841":"커뮤니케이션",
    "4860":"커뮤니케이션","4861":"커뮤니케이션","4899":"커뮤니케이션",
    "7810":"커뮤니케이션","7812":"커뮤니케이션","7820":"커뮤니케이션",
    "7941":"커뮤니케이션","7948":"커뮤니케이션","7990":"커뮤니케이션",
    "7993":"커뮤니케이션","7999":"커뮤니케이션",
    # 금융
    "6000":"금융","6020":"금융","6021":"금융","6022":"금융","6035":"금융",
    "6036":"금융","6099":"금융","6110":"금융","6141":"금융","6150":"금융",
    "6160":"금융","6162":"금융","6199":"금융","6200":"금융","6211":"금융",
    "6280":"금융","6282":"금융","6300":"금융","6311":"금융","6321":"금융",
    "6324":"금융","6331":"금융","6351":"금융","6361":"금융","6371":"금융",
    "6411":"금융","6710":"금융","6719":"금융","6726":"금융","6798":"금융",
    # 부동산
    "6500":"부동산","6510":"부동산","6512":"부동산","6513":"부동산",
    "6530":"부동산","6531":"부동산","6552":"부동산","6700":"부동산",
    # 헬스케어
    "2830":"헬스케어","2833":"헬스케어","2834":"헬스케어","2835":"헬스케어",
    "2836":"헬스케어","3826":"헬스케어","3841":"헬스케어","3842":"헬스케어",
    "3845":"헬스케어","5122":"헬스케어","8000":"헬스케어","8011":"헬스케어",
    "8049":"헬스케어","8060":"헬스케어","8062":"헬스케어","8099":"헬스케어",
    # 경기소비재
    "2300":"경기소비재","2510":"경기소비재","2511":"경기소비재",
    "3630":"경기소비재","3651":"경기소비재","3711":"경기소비재",
    "3714":"경기소비재","3751":"경기소비재","5511":"경기소비재",
    "5531":"경기소비재","5600":"경기소비재","5621":"경기소비재",
    "5651":"경기소비재","5712":"경기소비재","5731":"경기소비재",
    "5900":"경기소비재","5941":"경기소비재","7011":"경기소비재",
    "7510":"경기소비재","7514":"경기소비재","7532":"경기소비재",
    # 필수소비재
    "2000":"필수소비재","2011":"필수소비재","2020":"필수소비재",
    "2040":"필수소비재","2050":"필수소비재","2080":"필수소비재",
    "2082":"필수소비재","2086":"필수소비재","2090":"필수소비재",
    "2100":"필수소비재","2111":"필수소비재","2840":"필수소비재",
    "2844":"필수소비재","5140":"필수소비재","5411":"필수소비재",
    "5412":"필수소비재","5461":"필수소비재",
    # 에너지
    "1300":"에너지","1311":"에너지","1321":"에너지","1381":"에너지",
    "1382":"에너지","2900":"에너지","2911":"에너지","5171":"에너지",
    "5172":"에너지",
    # 소재
    "1040":"소재","1400":"소재","2600":"소재","2611":"소재","2621":"소재",
    "2800":"소재","2812":"소재","2819":"소재","2821":"소재","2869":"소재",
    "3310":"소재","3312":"소재","3334":"소재","3350":"소재","3357":"소재",
    "2400":"소재","2411":"소재","2421":"소재",
    # 산업재
    "1520":"산업재","1521":"산업재","1542":"산업재","1600":"산업재",
    "1711":"산업재","1731":"산업재","1799":"산업재","3441":"산업재",
    "3443":"산업재","3511":"산업재","3531":"산업재","3533":"산업재",
    "3559":"산업재","3561":"산업재","3564":"산업재","3569":"산업재",
    "3599":"산업재","3612":"산업재","3621":"산업재","3699":"산업재",
    "3724":"산업재","3731":"산업재","3764":"산업재","4213":"산업재",
    "4412":"산업재","4512":"산업재","4522":"산업재","4724":"산업재",
    "4731":"산업재","7381":"산업재","7389":"산업재","8711":"산업재",
    "8721":"산업재","8731":"산업재","8742":"산업재",
    # 유틸리티
    "4900":"유틸리티","4911":"유틸리티","4922":"유틸리티","4924":"유틸리티",
    "4931":"유틸리티","4932":"유틸리티","4941":"유틸리티","4952":"유틸리티",
    "4961":"유틸리티","4991":"유틸리티",
}

def get_sector(sic_code) -> str:
    return SIC_TO_GICS.get(str(sic_code), "UNKNOWN")
```

**UNKNOWN 섹터 폴백 벤치마크 (S&P 500 전체 평균):**
```python
UNKNOWN_BENCHMARK = {
    "OPM": {"lo":8,"hi":20}, "ROE": {"lo":10,"hi":20},
    "DR":  {"lo":0,"hi":150},"CR":  {"lo":100,"hi":200},
    "ICR": {"lo":3,"hi":10}, "ROA": {"lo":5,"hi":15},
    "PER": {"lo":15,"hi":25},
}
```

---

*Skills_core.md v4.4.0 | SEC EDGAR 기반 | 6대 코어 스탯 | S/A/B/C 티어 시스템 | 데모모드(demo.db) | 동적 벤치마크(분위수 자동 계산) | 타깃: 투자 1~3년 차 30~40대 | 교육 목적 | 뇌동매매 하지 말고 알고 투자하자 | US Only | UI 규칙은 Skills_ui.md 참조*
