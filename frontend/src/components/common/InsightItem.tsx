interface Props {
  kind: 'strength' | 'caution' | 'qualitative';
  title: string;
  body: string;
}

const KIND_STYLE = {
  strength:   { icon: 'trending_up', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  caution:    { icon: 'warning',     color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20' },
  qualitative:{ icon: 'insights',    color: 'text-blue-400',    bg: 'bg-blue-500/10 border-blue-500/20' },
};

export default function InsightItem({ kind, title, body }: Props) {
  const { icon, color, bg } = KIND_STYLE[kind];
  return (
    <div className={`rounded-lg border p-4 ${bg}`}>
      <div className={`flex items-center gap-2 mb-2 ${color}`}>
        <span className="material-symbols-outlined text-base">{icon}</span>
        <span className="text-sm font-bold uppercase tracking-wide">{title}</span>
      </div>
      <p className="text-sm text-slate-400 leading-relaxed">{body}</p>
    </div>
  );
}
