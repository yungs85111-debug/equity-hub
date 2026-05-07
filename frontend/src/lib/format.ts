export function formatPercent(v: number | null | undefined, digits = 1): string {
  if (v == null) return 'N/A';
  return `${v.toFixed(digits)}%`;
}

export function formatRatio(v: number | null | undefined, digits = 1): string {
  if (v == null) return 'N/A';
  return `${v.toFixed(digits)}x`;
}

export function formatCurrency(v: number | null | undefined): string {
  if (v == null) return 'N/A';
  const abs = Math.abs(v);
  if (abs >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
  if (abs >= 1e9)  return `$${(v / 1e9).toFixed(2)}B`;
  if (abs >= 1e6)  return `$${(v / 1e6).toFixed(2)}M`;
  return `$${v.toFixed(0)}`;
}

export function formatMcap(v: number | null | undefined): string {
  return formatCurrency(v);
}

export function formatValue(v: number | null | undefined, unit: string): string {
  if (v == null) return 'N/A';
  if (unit === '%') return formatPercent(v);
  if (unit === 'x') return formatRatio(v);
  if (unit === '$') return formatCurrency(v);
  return String(v);
}
