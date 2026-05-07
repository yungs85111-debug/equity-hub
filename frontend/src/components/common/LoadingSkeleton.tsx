export default function LoadingSkeleton({ lines = 6 }: { lines?: number }) {
  return (
    <div className="p-8 space-y-4 animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-4 bg-slate-800 rounded" style={{ width: `${70 + (i % 3) * 10}%` }} />
      ))}
    </div>
  );
}
