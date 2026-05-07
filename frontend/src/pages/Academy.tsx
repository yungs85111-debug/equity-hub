import Layout from '../components/layout/Layout';
import { STAT_COLOR } from '../config/skills_config';

const STAT_GROUP: Record<string, string[]> = {
  profitability: ['opm', 'roe'],
  growth:        ['rev_yoy', 'rev_3y_cagr'],
  stability:     ['dr', 'icr'],
  efficiency:    ['asset_turn'],
  valuation:     ['per', 'ev_ebitda'],
  cash_power:    ['fcf_margin', 'net_cash'],
};

const STAT_LABEL: Record<string, string> = {
  profitability: '수익성',
  growth:        '성장성',
  stability:     '안정성',
  efficiency:    '효율성',
  valuation:     '밸류에이션',
  cash_power:    '현금창출력',
};

interface IndicatorMeta {
  fullname: string;
  definition: string;
  unit: string;
  caution_text?: string;
}

const META: Record<string, IndicatorMeta> = {
  opm:        { fullname: 'Operating Margin (영업이익률)',      unit: '%', definition: '매출에서 영업비용을 뺀 영업이익이 매출의 몇 %인가를 나타냅니다. 본업 수익성의 직접 지표입니다.' },
  roe:        { fullname: 'Return on Equity (자기자본이익률)',   unit: '%', definition: '주주가 투입한 자본 대비 회사가 얼마나 이익을 냈는지 보여줍니다. 자본 효율성의 핵심 지표입니다.', caution_text: '부채를 많이 쓰면 ROE가 인위적으로 높아질 수 있어 DR과 함께 봐야 합니다.' },
  dr:         { fullname: 'Debt Ratio (부채비율)',               unit: '%', definition: '총부채를 자기자본으로 나눈 비율로, 재무 레버리지의 강도를 나타냅니다.', caution_text: '은행·금융업은 사업 구조상 부채비율이 매우 높은 것이 정상이라 직접 비교가 어렵습니다.' },
  icr:        { fullname: 'Interest Coverage Ratio (이자보상배율)', unit: 'x', definition: '영업이익을 이자비용으로 나눈 값으로, 회사가 이자를 갚을 여력을 보여줍니다.' },
  rev_yoy:    { fullname: 'Revenue YoY (매출 전년 대비)',        unit: '%', definition: '직전 연도 대비 매출 성장률입니다. 단기 모멘텀의 직관적 지표입니다.' },
  rev_3y_cagr:{ fullname: 'Revenue 3Y CAGR (3년 연평균 성장률)', unit: '%', definition: '지난 3년간 매출의 연평균 성장률입니다. 장기 성장 추세를 봅니다.' },
  asset_turn: { fullname: 'Asset Turnover (자산회전율)',         unit: 'x', definition: '자산 1단위로 얼마의 매출을 만들었는지 보여주는 효율성 지표입니다.' },
  per:        { fullname: 'Price to Earnings (주가수익비율)',    unit: 'x', definition: '주가를 주당순이익으로 나눈 값입니다. 투자자가 1달러 이익에 얼마를 지불하는가를 봅니다.', caution_text: '적자 기업은 PER 산출이 무의미합니다. 산업 평균과 비교해야 의미가 있습니다.' },
  ev_ebitda:  { fullname: 'EV/EBITDA (기업가치 배수)',          unit: 'x', definition: '기업가치를 영업이익+감가상각비로 나눈 값으로, 자본구조가 다른 회사 비교에 적합합니다.' },
  fcf_margin: { fullname: 'Free Cash Flow Margin (잉여현금흐름률)', unit: '%', definition: '매출 1달러당 자유롭게 쓸 수 있는 현금이 얼마인가를 나타냅니다.' },
  net_cash:   { fullname: 'Net Cash (순현금)',                  unit: '$', definition: '보유 현금에서 부채를 뺀 값입니다. 양수면 무차입 경영입니다.' },
};

const TIER_ROWS = [
  { tier: 'S', color: '#22C55E', score: '80점 이상', desc: '동종 섹터 상위 10~20% 수준의 우수한 재무 구조' },
  { tier: 'A', color: '#60A5FA', score: '65~79점',   desc: '섹터 평균을 상회하는 안정적 재무 체력' },
  { tier: 'B', color: '#F59E0B', score: '45~64점',   desc: '섹터 평균 수준, 개선 여지가 있는 상태' },
  { tier: 'C', color: '#EF4444', score: '44점 이하', desc: '재무 지표가 섹터 평균 대비 부진, 주의 필요' },
];

export default function Academy() {
  return (
    <Layout>
      <div className="px-6 py-6 max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-xl font-black text-slate-100 tracking-tight mb-1">ACADEMY</h1>
          <p className="text-xs text-slate-500">EQUITY HUB에서 사용하는 지표 정의와 티어 기준을 설명합니다.</p>
        </div>

        {/* 티어 기준 */}
        <section className="mb-10">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">티어 기준</h2>
          <div className="card overflow-hidden">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500">
                  <th className="text-left p-3 w-12">티어</th>
                  <th className="text-left p-3 w-24">총점</th>
                  <th className="text-left p-3">설명</th>
                </tr>
              </thead>
              <tbody>
                {TIER_ROWS.map(({ tier, color, score, desc }) => (
                  <tr key={tier} className="border-b border-slate-800/50">
                    <td className="p-3">
                      <span className="text-base font-black italic" style={{ color }}>{tier}</span>
                    </td>
                    <td className="p-3 text-slate-400">{score}</td>
                    <td className="p-3 text-slate-500">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[10px] text-slate-600 mt-2">
            총점 = 공통점수(40%) × 0.4 + 섹터점수(60%) × 0.6 · 섹터점수는 동종 섹터 내 백분위 기반
          </p>
        </section>

        {/* 6대 스탯 × 지표 */}
        <section>
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">6대 코어 스탯 · 지표 사전</h2>
          <div className="space-y-6">
            {Object.entries(STAT_GROUP).map(([statKey, indicators]) => (
              <div key={statKey}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 rounded-full" style={{ background: STAT_COLOR[statKey] }} />
                  <h3 className="text-sm font-bold" style={{ color: STAT_COLOR[statKey] }}>
                    {STAT_LABEL[statKey]}
                  </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {indicators.map(key => {
                    const m = META[key];
                    if (!m) return null;
                    return (
                      <div key={key} className="card p-4 hover:border-slate-600 transition-colors">
                        <div className="flex items-start justify-between mb-2">
                          <p className="text-xs font-bold text-slate-200 leading-snug">{m.fullname}</p>
                          <span className="text-[9px] text-slate-600 border border-slate-700 rounded px-1.5 py-0.5 ml-2 shrink-0">{m.unit}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">{m.definition}</p>
                        {m.caution_text && (
                          <div className="mt-2 border-t border-slate-800 pt-2">
                            <p className="text-[10px] text-amber-400/70 leading-relaxed">⚠️ {m.caution_text}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 데이터 출처 */}
        <section className="mt-10 card p-4 bg-slate-950/50">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">데이터 출처</h2>
          <ul className="space-y-1 text-[11px] text-slate-500">
            <li>· <strong className="text-slate-400">재무 데이터</strong>: SEC EDGAR 10-K 연간 보고서 (XBRL)</li>
            <li>· <strong className="text-slate-400">시세·밸류에이션</strong>: Yahoo Finance (PER, PBR, 시가총액, 주가 등락률)</li>
            <li>· <strong className="text-slate-400">대상 종목</strong>: S&amp;P 500 / NASDAQ 100 기준 190개 종목</li>
            <li>· <strong className="text-slate-400">기준 연도</strong>: FY2025 (회계연도 2025년 연간 보고서)</li>
          </ul>
        </section>
      </div>
    </Layout>
  );
}
