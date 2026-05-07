interface Props { priceDate?: string | null; }

export default function DemoBanner({ priceDate }: Props) {
  return (
    <div className="w-full bg-slate-900/70 border-b border-amber-500/30 px-6 py-2.5 flex items-center justify-between">
      <span className="text-xs font-bold text-amber-300 uppercase tracking-widest">
        📅 데이터 기준: {priceDate ?? '—'}&nbsp;|&nbsp;출처: SEC EDGAR
      </span>
      <span className="text-xs font-bold text-amber-400/70 uppercase tracking-widest">
        데모 버전 — 실시간 데이터가 아닙니다
      </span>
    </div>
  );
}
