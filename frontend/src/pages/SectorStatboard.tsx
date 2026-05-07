import { useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import type { SectorDetailResponse } from '../types';
import { STAT_COLOR, STAT_LABEL_KO, INDICATOR_LABEL_KO, TIER_COLOR, METRIC_DIRECTION } from '../config/skills_config';
import { tierHex } from '../lib/tier';
import { formatPercent, formatRatio } from '../lib/format';
import Layout from '../components/layout/Layout';
import TierBadge from '../components/common/TierBadge';
import BenchmarkSourceLabel from '../components/common/BenchmarkSourceLabel';
import InsightItem from '../components/common/InsightItem';
import LoadingSkeleton from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';

type Tab = 'understand' | 'compare';

// ── Stat card for Tab 1 ──────────────────────────────────────────────────────
function StatCard({ statKey, avgStats }: { statKey: string; avgStats: Record<string, unknown> }) {
  const stat = avgStats[statKey] as Record<string, unknown> | undefined;
  const color = STAT_COLOR[statKey] ?? TIER_COLOR.UNKNOWN;
  const label = STAT_LABEL_KO[statKey] ?? statKey;
  if (!stat) return null;

  const tier = stat.tier as string | undefined;
  const metricEntries = Object.entries(stat).filter(([k]) => k !== 'source' && k !== 'tier');
  const tierColor = tier ? tierHex(tier) : '#475569';

  // 이 스탯의 방향이 모두 같은지 체크 (안내 문구용)
  const directions = metricEntries.map(([k]) => METRIC_DIRECTION[k]).filter(Boolean);
  const allUp   = directions.every(d => d === '↑');
  const allDown = directions.every(d => d === '↓');

  return (
    <div className="card p-4 hover:border-blue-500/30 transition-colors">
      {/* 헤더: 스탯명 + 티어 배지 */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
          <span className="text-sm font-bold uppercase tracking-wider" style={{ color }}>{label}</span>
        </div>
        {tier && <TierBadge tier={tier} size="sm" />}
      </div>

      {/* 지표 행 */}
      <div className="space-y-2.5">
        {metricEntries.map(([k, v]) => {
          return (
            <div key={k} className="flex justify-between items-center">
              <span className="text-xs text-slate-400">
                {INDICATOR_LABEL_KO[k] ?? k}
              </span>
              <span className="text-sm font-bold" style={{ color: tierColor }}>
                {v == null ? 'N/A' : typeof v === 'number' ? v.toFixed(1) : String(v)}
              </span>
            </div>
          );
        })}
      </div>

      {/* 방향 안내 + 출처 */}
      <div className="mt-3 pt-2.5 border-t border-slate-800 space-y-1">
        {(allUp || allDown) && (
          <p className="text-xs" style={{ color: allUp ? '#22C55E' : '#F59E0B' }}>
            {allUp ? '↑ 높을수록 좋음' : '↓ 낮을수록 좋음'}
          </p>
        )}
        <BenchmarkSourceLabel
          mode={(stat.source as string)?.includes('⚠️') ? 'fallback' : 'dynamic'}
          p50={metricEntries[0]?.[1] as number}
        />
      </div>
    </div>
  );
}

// ── Tier distribution bar ────────────────────────────────────────────────────
function TierDistBar({ dist }: { dist: SectorDetailResponse['tier_dist'] }) {
  return (
    <div className="card p-4">
      <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">티어 분포</h4>
      <div className="h-3 rounded-full overflow-hidden flex">
        <div style={{ width: `${dist.s_pct}%`, background: TIER_COLOR.S }} />
        <div style={{ width: `${dist.a_pct}%`, background: TIER_COLOR.A }} />
        <div style={{ width: `${dist.b_pct}%`, background: TIER_COLOR.B }} />
        <div style={{ width: `${dist.c_pct}%`, background: TIER_COLOR.C }} />
      </div>
      <div className="flex justify-between mt-2 text-xs text-slate-500">
        {[['S', dist.s_pct, TIER_COLOR.S], ['A', dist.a_pct, TIER_COLOR.A],
          ['B', dist.b_pct, TIER_COLOR.B], ['C', dist.c_pct, TIER_COLOR.C]].map(([t, p, c]) => (
          <span key={t as string} style={{ color: c as string }}>
            {t} {(p as number).toFixed(0)}%
          </span>
        ))}
      </div>
    </div>
  );
}

// ── Heatmap table ────────────────────────────────────────────────────────────
function HeatmapTable({ data }: { data: SectorDetailResponse }) {
  const nav = useNavigate();
  const rows = [...(data.top20 ?? []), ...(data.sector_avg_row ? [data.sector_avg_row] : [])];
  const STAT_KEYS = ['tier_profitability','tier_growth','tier_stability','tier_efficiency','tier_valuation','tier_cash_power'] as const;
  const STAT_NAMES = ['수익성','성장성','안정성','효율성','밸류에이션','현금창출력'];
  const STAT_COLORS = Object.values(STAT_COLOR);

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-slate-800">
            <th className="text-left p-3 text-slate-500 font-medium sticky left-0 bg-slate-900 min-w-[120px]">종목</th>
            {STAT_NAMES.map((n, i) => (
              <th key={n} className="p-2 text-center font-bold text-xs" style={{ color: STAT_COLORS[i] }}>{n}</th>
            ))}
            <th className="p-2 text-center text-slate-500 font-medium">총점</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => {
            const isAvgRow = row.ticker === 'SECTOR_AVG';
            return (
              <tr
                key={row.ticker}
                className={`border-b border-slate-800/50 transition-colors ${
                  isAvgRow
                    ? 'bg-slate-800/40 font-bold'
                    : 'hover:bg-slate-800/30 cursor-pointer'
                }`}
                onClick={() => !isAvgRow && nav(`/company/${row.ticker}`, { state: { sector: data.sector, tab: 'compare' } })}
              >
                <td className="p-3 sticky left-0 bg-slate-900">
                  <span className={isAvgRow ? 'text-slate-400' : 'text-blue-400 font-bold'}>{row.ticker}</span>
                  {!isAvgRow && <span className="ml-1 text-slate-500 truncate">{row.name}</span>}
                </td>
                {STAT_KEYS.map(k => {
                  const t = row[k] as string;
                  const color = tierHex(t);
                  return (
                    <td key={k} className="p-2 text-center">
                      <span className="inline-block text-xs font-bold px-2 py-0.5 rounded"
                        style={{ color, border: `1px solid ${color}40`, background: `${color}15` }}>
                        {t ?? '—'}
                      </span>
                    </td>
                  );
                })}
                <td className="p-2 text-center text-slate-300">
                  {row.total_score != null ? row.total_score.toFixed(0) : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── CAGR Top 3 ───────────────────────────────────────────────────────────────
function CagrTop3({ rows }: { data: SectorDetailResponse; rows: SectorDetailResponse['cagr_top3'] }) {
  return (
    <div className="card p-4">
      <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-3">3Y CAGR TOP 3</h4>
      <div className="space-y-3">
        {rows?.map((r, i) => (
          <div key={r.ticker} className="flex items-center gap-3">
            <span className="text-lg font-black text-slate-700">{i + 1}</span>
            <div className="flex-1">
              <span className="text-xs font-bold text-blue-400">{r.ticker}</span>
              <span className="ml-1 text-xs text-slate-500">{r.name}</span>
            </div>
            <span className="text-base font-bold text-emerald-400">{formatPercent(r.rev_3y_cagr)}</span>
          </div>
        ))}
        {!rows?.length && <p className="text-sm text-slate-600">데이터 없음</p>}
      </div>
    </div>
  );
}

// ── ROE × PER Scatter ────────────────────────────────────────────────────────
function ScatterPlot({ points }: { points: SectorDetailResponse['scatter'] }) {
  const valid = points?.filter(p => p.roe != null && p.per != null && p.per > 0 && p.per < 100) ?? [];
  const avgRoe = valid.length ? valid.reduce((s, p) => s + p.roe, 0) / valid.length : 0;

  return (
    <div className="card p-4">
      <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">ROE × PER 산점도</h4>
      <div className="relative h-48 border border-slate-800 rounded bg-slate-950/50 overflow-hidden">
        {/* Quadrant lines */}
        <div className="absolute inset-0 flex">
          <div className="flex-1 border-r border-slate-700/50" />
        </div>
        <div className="absolute inset-0 flex flex-col">
          <div className="flex-1 border-b border-slate-700/50" />
        </div>
        {/* Labels */}
        <span className="absolute top-1 right-2 text-xs text-amber-400/60">고ROE·고PER</span>
        <span className="absolute top-1 left-2 text-xs text-slate-600">저ROE·고PER</span>
        <span className="absolute bottom-1 right-2 text-xs text-emerald-400/60">고ROE·저PER</span>
        <span className="absolute bottom-1 left-2 text-xs text-slate-600">저ROE·저PER</span>
        {/* Points */}
        {valid.map(p => {
          const maxRoe = Math.max(...valid.map(v => v.roe));
          const x = Math.min(Math.max(((p.roe - (avgRoe - maxRoe * 0.3)) / (maxRoe * 1.6)) * 100, 5), 95);
          const y = Math.min(Math.max(((p.per - 5) / 80) * 100, 5), 95);
          return (
            <div
              key={p.ticker}
              className="absolute w-2 h-2 rounded-full bg-blue-400/60 border border-blue-400 cursor-pointer hover:bg-blue-400 transition-colors"
              style={{ left: `${x}%`, bottom: `${y}%`, transform: 'translate(-50%, 50%)' }}
              title={`${p.ticker} | ROE: ${formatPercent(p.roe)} | PER: ${formatRatio(p.per)}`}
            />
          );
        })}
      </div>
      <div className="flex justify-between mt-2 text-xs text-slate-600">
        <span>← 낮은 ROE</span><span>높은 ROE →</span>
      </div>
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function SectorStatboard() {
  const { sector_name } = useParams<{ sector_name: string }>();
  const location = useLocation();
  const initTab = (location.state as { tab?: Tab } | null)?.tab ?? 'understand';
  const [tab, setTab] = useState<Tab>(initTab);
  const sectorName = decodeURIComponent(sector_name ?? '');

  const { data, loading, error, refetch } = useApi<SectorDetailResponse>(
    `/sector/${encodeURIComponent(sectorName)}?tab=${tab}`,
    [sectorName, tab]
  );

  if (loading) return <Layout><LoadingSkeleton lines={12} /></Layout>;
  if (error || !data) return <Layout><ErrorState message={error?.message} onRetry={refetch} /></Layout>;

  return (
    <Layout priceDate={data.price_date} fiscalYear={data.fiscal_year} n={data.n}>
      <div className="px-6 py-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-black text-slate-100">{sectorName}</h1>
            <p className="text-sm text-slate-500 mt-1">{data.sector_intro}</p>
          </div>
          <TierBadge tier={data.overall_tier} size="lg" />
        </div>

        {/* Tab buttons */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab('understand')}
            className={`text-sm px-4 py-2 rounded transition-colors font-medium ${
              tab === 'understand' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-slate-500 hover:text-slate-300 border border-slate-800'
            }`}
          >
            섹터 이해하기
          </button>
          <button
            onClick={() => setTab('compare')}
            className={`text-sm px-4 py-2 rounded transition-colors font-medium ${
              tab === 'compare' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-slate-500 hover:text-slate-300 border border-slate-800'
            }`}
          >
            종목 비교 →
          </button>
        </div>

        {tab === 'understand' && (
          <div className="space-y-6">
            {/* 6대 스탯 카드 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {['profitability','growth','stability','efficiency','valuation','cash_power'].map(k => (
                <StatCard key={k} statKey={k} avgStats={data.avg_stats} />
              ))}
            </div>

            {/* 티어 분포 + 인사이트 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <TierDistBar dist={data.tier_dist} />
              <InsightItem kind="qualitative" title="섹터 인사이트" body={data.auto_insight} />
            </div>
          </div>
        )}

        {tab === 'compare' && (
          <div className="space-y-6">
            <HeatmapTable data={data} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.cagr_top3 && <CagrTop3 data={data} rows={data.cagr_top3} />}
              {data.scatter && <ScatterPlot points={data.scatter} />}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
