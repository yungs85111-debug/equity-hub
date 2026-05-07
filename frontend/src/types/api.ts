import type { Tier, StatKey } from './domain';

export interface HealthResponse {
  status: string;
  data_mode: string;
  price_date: string | null;
}

export interface SectorSummary {
  sector: string;
  n: number;
  avg_score: number;
  overall_tier: Tier;
  n_s: number; n_a: number; n_b: number; n_c: number;
  s_pct: number; a_pct: number; b_pct: number; c_pct: number;
  price_date: string | null;
}

export interface SectorsResponse {
  sectors: SectorSummary[];
  fiscal_year: number;
  price_date: string | null;
}

export interface AvgStat {
  source: string;
  tier?: string;
  [key: string]: number | string | null | undefined;
}

export interface KeyIndicatorDetail {
  indicator: string;
  sector_avg: number | null;
  source: string;
}

export interface TierDist {
  n: number;
  n_s: number; n_a: number; n_b: number; n_c: number;
  s_pct: number; a_pct: number; b_pct: number; c_pct: number;
}

export interface HeatmapRow {
  ticker: string;
  name: string;
  market_cap: number | null;
  tier_profitability: Tier;
  tier_growth: Tier;
  tier_stability: Tier;
  tier_efficiency: Tier;
  tier_valuation: Tier;
  tier_cash_power: Tier;
  total_score: number | null;
  overall_tier: Tier | null;
  rev_3y_cagr: number | null;
  roe: number | null;
  per: number | null;
}

export interface CagrTop3Row {
  ticker: string;
  name: string;
  rev_3y_cagr: number;
}

export interface ScatterPoint {
  ticker: string;
  roe: number;
  per: number;
}

export interface SectorDetailResponse {
  sector: string;
  n: number;
  fiscal_year: number;
  price_date: string | null;
  sector_intro: string;
  key_indicators: string[];
  key_indicator_details: KeyIndicatorDetail[];
  avg_stats: Record<StatKey, AvgStat>;
  tier_dist: TierDist;
  auto_insight: string;
  source_label: string;
  overall_tier: Tier;
  // tab=compare
  top20?: HeatmapRow[];
  sector_avg_row?: HeatmapRow;
  cagr_top3?: CagrTop3Row[];
  scatter?: ScatterPoint[];
}

export interface SixCoreStat {
  stat: StatKey;
  tier: Tier;
  bar_width: number;
  values: Record<string, number | null>;
}

export interface KPI {
  label: string;
  value: number | null;
  unit: string;
  indicator: string;
}

export interface InsightItem {
  kind: 'strength' | 'caution' | 'qualitative';
  title: string;
  body: string;
}

export interface CompanyDetailResponse {
  ticker: string;
  name: string;
  sector: string;
  exchange: string | null;
  gics_industry: string | null;
  cik: string | null;
  fiscal_year: number;
  price_date: string | null;
  stock_price: number | null;
  market_cap: number | null;
  price_change_1y: number | null;
  total_score: number;
  overall_tier: Tier;
  sector_percentile: number;
  tiers: Record<string, Tier>;
  six_core: SixCoreStat[];
  kpis: KPI[];
  insights: InsightItem[];
}

export interface Percentiles {
  p10: number; p25: number; p50: number; p75: number; p90: number;
}

export interface IndicatorPopupResponse {
  ticker: string;
  indicator_name: string;
  indicator_fullname: string;
  value: number | null;
  tier: Tier | null;
  unit: string;
  sector: string;
  sector_avg: number | null;
  lo: number | null;
  hi: number | null;
  percentile: number | null;
  percentiles: Partial<Percentiles>;
  n: number;
  source_mode: 'dynamic' | 'fallback';
  source_label: string;
  definition: string;
  caution_text: string | null;
  price_date: string | null;
  fiscal_year: number;
}
