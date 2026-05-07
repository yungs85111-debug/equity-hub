import { STAT_COLOR, STAT_LABEL_KO, TIER_COLOR } from '../../config/skills_config';
import TierBadge from './TierBadge';

interface Props {
  stat: string;
  tier: string | null | undefined;
  barWidth: number;       // 0–100
  valueStr?: string;
  onClick?: () => void;
}

export default function StatBar({ stat, tier, barWidth, valueStr, onClick }: Props) {
  const color = STAT_COLOR[stat] ?? TIER_COLOR.UNKNOWN;
  const label = STAT_LABEL_KO[stat] ?? stat;

  return (
    <div
      className={`flex items-center gap-3 py-2 ${onClick ? 'cursor-pointer hover:bg-slate-800/50 rounded px-2 -mx-2' : ''}`}
      onClick={onClick}
    >
      <span className="text-xs text-slate-400 w-20 shrink-0">{label}</span>
      <div className="flex-1 bg-slate-800 rounded-full h-2 relative overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 bar-${stat}`}
          style={{ width: `${Math.max(barWidth, 2)}%`, backgroundColor: color }}
        />
      </div>
      <TierBadge tier={tier} size="sm" />
      {valueStr && <span className="text-xs text-slate-400 w-16 text-right">{valueStr}</span>}
      {onClick && <span className="material-symbols-outlined text-slate-600 text-sm">chevron_right</span>}
    </div>
  );
}
