import { useNavigate } from 'react-router-dom';
import type { SectorSummary } from '../../types';
import { TIER_COLOR } from '../../config/skills_config';
import TierBadge from '../common/TierBadge';

interface Props { data: SectorSummary; }

export default function SectorCard({ data }: Props) {
  const nav = useNavigate();
  const { sector, n, avg_score, overall_tier, s_pct, a_pct, b_pct, c_pct } = data;

  return (
    <div
      onClick={() => nav(`/sector/${encodeURIComponent(sector)}`)}
      className="card hud-corner p-5 cursor-pointer hover:bg-slate-800/60 hover:border-blue-500/30 transition-all group"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-base font-bold text-slate-200 group-hover:text-white">{sector}</h3>
          <p className="text-sm text-slate-500 mt-0.5">{n}개 종목 분석</p>
        </div>
        <TierBadge tier={overall_tier} size="md" />
      </div>

      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-slate-500">평균 총점</span>
        <span className="text-base font-bold text-slate-300">{avg_score.toFixed(0)}점</span>
      </div>

      {/* 4색 분포 바 */}
      <div className="h-2 w-full rounded-full overflow-hidden flex">
        <div style={{ width: `${s_pct}%`, background: TIER_COLOR.S }} />
        <div style={{ width: `${a_pct}%`, background: TIER_COLOR.A }} />
        <div style={{ width: `${b_pct}%`, background: TIER_COLOR.B }} />
        <div style={{ width: `${c_pct}%`, background: TIER_COLOR.C }} />
      </div>
      <div className="flex justify-between mt-1.5 text-xs text-slate-500">
        <span>S {s_pct.toFixed(0)}%</span>
        <span>A {a_pct.toFixed(0)}%</span>
        <span>B {b_pct.toFixed(0)}%</span>
        <span>C {c_pct.toFixed(0)}%</span>
      </div>

      <div className="mt-3 flex items-center text-sm text-slate-500 group-hover:text-blue-400 transition-colors">
        <span>섹터 분석 보기</span>
        <span className="material-symbols-outlined text-base ml-1">chevron_right</span>
      </div>
    </div>
  );
}
