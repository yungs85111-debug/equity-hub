import { useParams, useLocation, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { useIndicatorPopup } from '../hooks/useIndicatorPopup';
import type { CompanyDetailResponse } from '../types';
import { STAT_LABEL_KO, INDICATOR_LABEL_KO, STAT_COLOR, TIER_COLOR } from '../config/skills_config';
import { formatPercent, formatCurrency, formatValue } from '../lib/format';
import { tierHex } from '../lib/tier';
import Layout from '../components/layout/Layout';
import TierBadge from '../components/common/TierBadge';
import InsightItem from '../components/common/InsightItem';
import LoadingSkeleton from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';
import IndicatorPopup from '../components/popup/IndicatorPopup';

export default function CompanyDetail() {
  const { ticker } = useParams<{ ticker: string }>();
  const location = useLocation();
  const fromState = location.state as { sector?: string; tab?: string } | null;
  const fromCompare = fromState?.tab === 'compare';

  const { data, loading, error, refetch } = useApi<CompanyDetailResponse>(
    `/company/${ticker?.toUpperCase()}`, [ticker]
  );
  const popup = useIndicatorPopup();

  if (loading) return <Layout><LoadingSkeleton lines={14} /></Layout>;
  if (error || !data) return <Layout><ErrorState message={error?.message} onRetry={refetch} /></Layout>;

  const sectorPath = `/sector/${encodeURIComponent(data.sector)}`;

  return (
    <Layout priceDate={data.price_date} fiscalYear={data.fiscal_year}>
      <div className="px-6 py-6 max-w-7xl mx-auto">

        {/* ── Breadcrumb ── */}
        <nav className="flex items-center gap-1.5 text-sm mb-5">
          <Link to="/" className="text-slate-500 hover:text-slate-300 transition-colors">
            섹터 허브
          </Link>
          <span className="text-slate-700">›</span>
          <Link
            to={sectorPath}
            state={fromCompare ? { tab: 'compare' } : undefined}
            className="hover:text-slate-300 transition-colors"
            style={{ color: fromCompare ? '#60A5FA' : undefined }}
          >
            {data.sector}{fromCompare && ' · 종목 비교'}
          </Link>
          <span className="text-slate-700">›</span>
          <span className="text-slate-300 font-medium">{data.ticker}</span>
        </nav>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-4">
          {/* Profile card — col-span-8 */}
          <div className="md:col-span-8 card hud-corner p-5">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl font-black text-blue-400">{data.ticker}</span>
                  <span className="text-sm text-slate-500">{data.exchange}</span>
                </div>
                <h2 className="text-lg font-bold text-slate-200 mb-1">{data.name}</h2>
                <div className="flex gap-2">
                  <span className="text-xs px-2 py-0.5 rounded border border-slate-700 text-slate-500">{data.sector}</span>
                  {data.gics_industry && (
                    <span className="text-xs px-2 py-0.5 rounded border border-slate-700 text-slate-600 hidden lg:block">{data.gics_industry}</span>
                  )}
                </div>
              </div>
              <div className="text-right text-sm text-slate-500">
                <p className="text-base font-bold text-slate-200">{formatCurrency(data.market_cap)}</p>
                <p>시가총액</p>
                {data.price_change_1y != null && (
                  <p className={data.price_change_1y >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                    1Y {formatPercent(data.price_change_1y)}
                  </p>
                )}
              </div>
            </div>

            {/* Power level bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>POWER LEVEL</span>
                <span>{data.total_score.toFixed(0)} / 100</span>
              </div>
              <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all"
                  style={{ width: `${data.total_score}%` }} />
              </div>
            </div>
          </div>

          {/* Overall tier — col-span-4 */}
          <div className="md:col-span-4 card p-5 flex flex-col items-center justify-center text-center gap-2">
            <span className="text-xs text-slate-500 uppercase tracking-widest">Overall Tier</span>
            <span
              className="text-6xl font-black italic tracking-tighter"
              style={{ color: tierHex(data.overall_tier) }}
            >
              {data.overall_tier}
            </span>
            <p className="text-sm text-slate-400">{data.total_score.toFixed(0)}점</p>
            <p className="text-xs text-slate-600">섹터 내 상위 {(100 - data.sector_percentile).toFixed(0)}%</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-4">
          {/* 6대 코어 스탯 — col-span-7 */}
          <div className="md:col-span-7 card p-5">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">6대 코어 스탯</h3>
            <div className="space-y-1">
              {data.six_core.map(s => {
                const color = STAT_COLOR[s.stat] ?? TIER_COLOR.UNKNOWN;
                const label = STAT_LABEL_KO[s.stat];
                const metrics = Object.entries(s.values)
                  .filter(([, v]) => v != null)
                  .map(([k, v]) => `${INDICATOR_LABEL_KO[k] ?? k}: ${typeof v === 'number' ? v.toFixed(1) : v}`)
                  .join(' · ');

                return (
                  <div
                    key={s.stat}
                    className="flex items-center gap-3 py-2 cursor-pointer hover:bg-slate-800/50 rounded px-2 -mx-2"
                    onClick={() => popup.openPopup(data.ticker, Object.keys(s.values)[0] ?? s.stat)}
                  >
                    <div className="w-1 h-1 rounded-full shrink-0" style={{ background: color }} />
                    <span className="text-sm text-slate-400 w-20 shrink-0">{label}</span>
                    <div className="flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div className="h-full rounded-full"
                        style={{ width: `${Math.max(s.bar_width, 2)}%`, background: color }} />
                    </div>
                    <TierBadge tier={s.tier} size="sm" />
                    <span className="text-xs text-slate-600 text-right hidden lg:block max-w-[120px] truncate">{metrics}</span>
                    <span className="material-symbols-outlined text-slate-700 text-sm">info</span>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-slate-600 mt-3">※ 지표명을 클릭하면 상세 설명이 열립니다</p>
          </div>

          {/* Insights + 교육 배너 — col-span-5 */}
          <div className="md:col-span-5 flex flex-col gap-3">
            {data.insights.map((ins, i) => (
              <InsightItem key={i} kind={ins.kind} title={ins.title} body={ins.body} />
            ))}
            {/* 교육 배너 */}
            <div className="card p-4 border-amber-500/20 bg-amber-500/5">
              <p className="text-xs text-amber-400/80 leading-relaxed">
                ⚠️ 이 페이지는 <strong>교육 목적</strong>으로 제작되었습니다.
                투자 추천·매수·매도 의견이 아닙니다.
                전문 투자 도구나 전문가 의견을 대체하지 않습니다.
              </p>
            </div>
          </div>
        </div>

        {/* KPI 4개 하단 바 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {data.kpis.map(kpi => (
            <div
              key={kpi.indicator}
              className="card p-4 cursor-pointer hover:border-blue-500/30 transition-colors"
              onClick={() => popup.openPopup(data.ticker, kpi.indicator)}
            >
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{kpi.label}</p>
              <p className="text-lg font-bold text-slate-200">{formatValue(kpi.value, kpi.unit)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Indicator popup */}
      {popup.open && (
        <IndicatorPopup
          ticker={popup.ticker}
          indicator={popup.indicator}
          onClose={popup.closePopup}
        />
      )}
    </Layout>
  );
}
