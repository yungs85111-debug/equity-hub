// [데모 고정값] 라벨 — Market Pulse, HUD Ticker 영역에 필수
export default function DemoFixedTag({ label = '데모 고정값' }: { label?: string }) {
  return (
    <span className="text-[9px] font-bold uppercase tracking-widest text-amber-400/60 border border-amber-500/20 px-1.5 py-0.5 rounded">
      [{label}]
    </span>
  );
}
