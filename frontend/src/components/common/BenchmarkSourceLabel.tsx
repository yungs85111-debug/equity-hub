interface Props {
  mode: 'dynamic' | 'fallback';
  n?: number;
  fiscalYear?: number;
  p50?: number | null;
}

export default function BenchmarkSourceLabel({ mode, n, fiscalYear = 2025, p50 }: Props) {
  if (mode === 'fallback') {
    return (
      <span className="text-xs text-amber-400/80">
        ⚠️ 섹터 데이터 부족 — S&amp;P 500 평균 기준 적용
      </span>
    );
  }
  return (
    <span className="text-xs text-slate-500">
      섹터 중앙값 {p50 != null ? p50.toFixed(1) : '—'} · 실측 {n}개사 · {fiscalYear}년 기준
    </span>
  );
}
