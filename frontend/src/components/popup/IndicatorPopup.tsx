import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useApi } from '../../hooks/useApi';
import type { IndicatorPopupResponse } from '../../types';
import { tierHex } from '../../lib/tier';
import { TIER_COLOR } from '../../config/skills_config';
import { formatValue } from '../../lib/format';
import TierBadge from '../common/TierBadge';
import BenchmarkSourceLabel from '../common/BenchmarkSourceLabel';
import LoadingSkeleton from '../common/LoadingSkeleton';

interface Props { ticker: string; indicator: string; onClose: () => void; }

function BenchmarkBar({ data }: { data: IndicatorPopupResponse }) {
  const { percentiles: p, value, sector_avg } = data;
  if (!p.p10 && !p.p50) return null;
  const bars = [
    { label: 'P10', val: p.p10, color: TIER_COLOR.C },
    { label: 'P25', val: p.p25, color: TIER_COLOR.B },
    { label: 'P50', val: p.p50, color: TIER_COLOR.A },
    { label: 'P75', val: p.p75, color: TIER_COLOR.S },
    { label: 'P90', val: p.p90, color: TIER_COLOR.S },
  ];
  const max = Math.max(...bars.map(b => b.val ?? 0), value ?? 0, sector_avg ?? 0, 1);

  return (
    <div>
      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">벤치마크 분포</h4>
      <div className="space-y-2">
        {bars.map(({ label, val, color }) => val != null && (
          <div key={label} className="flex items-center gap-2">
            <span className="text-xs text-slate-500 w-8 shrink-0">{label}</span>
            <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${(val / max) * 100}%`, background: color }} />
            </div>
            <span className="text-xs text-slate-400 w-16 text-right">{formatValue(val, data.unit)}</span>
          </div>
        ))}
        {value != null && (
          <div className="flex items-center gap-2 mt-2 border-t border-slate-800 pt-2">
            <span className="text-xs font-bold w-8 shrink-0" style={{ color: tierHex(data.tier) }}>현재</span>
            <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${Math.min((value / max) * 100, 100)}%`, background: tierHex(data.tier) }} />
            </div>
            <span className="text-xs font-bold w-16 text-right" style={{ color: tierHex(data.tier) }}>
              {formatValue(value, data.unit)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

function PopupContent({ data, onClose }: { data: IndicatorPopupResponse; onClose: () => void }) {
  return (
    <div className="card hud-corner w-full max-w-2xl mx-4 shadow-2xl border-slate-700 max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-start justify-between p-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-base font-bold text-slate-200">{data.indicator_fullname}</h2>
            <TierBadge tier={data.tier} size="sm" />
          </div>
          <p className="text-sm text-slate-500">{data.ticker} · {data.sector} · {data.fiscal_year}년 기준</p>
        </div>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-200 transition-colors ml-4">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      {/* Body 2-column */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-5">
        {/* 좌측 */}
        <div className="space-y-4">
          {/* Current value */}
          <div className="card p-4 bg-slate-950/50">
            <p className="text-xs text-slate-500 mb-1">현재 수치</p>
            <p className="text-3xl font-black" style={{ color: tierHex(data.tier) }}>
              {formatValue(data.value, data.unit)}
            </p>
            {data.percentile != null && (
              <p className="text-sm text-slate-500 mt-1">섹터 내 상위 {(100 - data.percentile).toFixed(0)}%</p>
            )}
          </div>

          {/* 섹터 평균 / 정상 범위 */}
          <div className="card p-4 bg-slate-950/50">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-500">섹터 평균</span>
              <span className="font-bold text-slate-300">{formatValue(data.sector_avg, data.unit)}</span>
            </div>
            {data.lo != null && data.hi != null && (
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-500">정상 범위</span>
                <span className="text-slate-400">{formatValue(data.lo, data.unit)} ~ {formatValue(data.hi, data.unit)}</span>
              </div>
            )}
            <div className="mt-1">
              <BenchmarkSourceLabel
                mode={data.source_mode}
                n={data.n}
                fiscalYear={data.fiscal_year}
                p50={data.percentiles.p50}
              />
            </div>
          </div>

          {/* 지표 정의 */}
          <div>
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">지표 정의</h4>
            <p className="text-sm text-slate-400 leading-relaxed">{data.definition}</p>
          </div>

          {/* 주의사항 */}
          {data.caution_text && (
            <div className="border border-amber-500/20 rounded-lg p-3 bg-amber-500/5">
              <p className="text-sm text-amber-400/80 leading-relaxed">
                ⚠️ {data.caution_text}
              </p>
            </div>
          )}
        </div>

        {/* 우측 */}
        <div className="space-y-4">
          <BenchmarkBar data={data} />

          <div className="flex flex-col gap-2 mt-4">
            <a
              href={`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${data.ticker}&type=10-K&dateb=&owner=include&count=5`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm border border-slate-700 px-4 py-2.5 rounded hover:bg-slate-800 transition-colors text-slate-400 text-center flex items-center justify-center gap-1.5"
            >
              <span className="material-symbols-outlined text-base">open_in_new</span>
              SEC EDGAR 원문 (10-K)
            </a>
          </div>
        </div>
      </div>

      {/* 하단 면책 */}
      <div className="px-5 pb-4 border-t border-slate-800 pt-3">
        <p className="text-xs text-slate-600">
          ⚠️ 교육 목적 | 투자 추천 아님 | SEC EDGAR 데이터 | {data.price_date} 기준
        </p>
      </div>
    </div>
  );
}

export default function IndicatorPopup({ ticker, indicator, onClose }: Props) {
  const { data, loading } = useApi<IndicatorPopupResponse>(
    `/indicator/${ticker}/${indicator}`, [ticker, indicator]
  );

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-xl bg-slate-950/40"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      {loading || !data
        ? <div className="card p-8 w-80"><LoadingSkeleton lines={5} /></div>
        : <PopupContent data={data} onClose={onClose} />
      }
    </div>,
    document.body
  );
}
