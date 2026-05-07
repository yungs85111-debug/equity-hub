import { tierHex } from '../../lib/tier';

interface Props {
  tier: string | null | undefined;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  score?: number | null;
  italic?: boolean;
}

const SIZE = {
  sm: 'text-xs px-2 py-0.5 rounded',
  md: 'text-sm px-2.5 py-0.5 rounded font-bold',
  lg: 'text-3xl px-3 py-1 rounded-md',
  xl: 'text-5xl italic font-black tracking-tighter px-4 py-2',
};

export default function TierBadge({ tier, size = 'md', score, italic }: Props) {
  const color = tierHex(tier);
  const label = tier ?? '—';

  return (
    <span
      className={`inline-flex flex-col items-center font-bold uppercase tracking-wider ${SIZE[size]}`}
      style={{ color, border: `1px solid ${color}40`, background: `${color}15` }}
    >
      <span className={italic ? 'italic' : ''}>{label}</span>
      {score != null && (
        <span className="text-xs font-normal not-italic opacity-70">{score.toFixed(0)}점</span>
      )}
    </span>
  );
}
