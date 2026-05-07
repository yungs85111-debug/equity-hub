// Skills §12 tier colors — single source of truth
export const TIER_COLOR: Record<string, string> = {
  S:        '#22C55E',
  A:        '#60A5FA',
  B:        '#F59E0B',
  C:        '#EF4444',
  IMPAIRED: '#7C3AED',
  DEBT_FREE:'#60A5FA',
  UNKNOWN:  '#475569',
};

// 6-stat axis colors — §4-1
export const STAT_COLOR: Record<string, string> = {
  profitability: '#3B82F6',
  growth:        '#10B981',
  stability:     '#F59E0B',
  efficiency:    '#8B5CF6',
  valuation:     '#EC4899',
  cash_power:    '#06B6D4',
};

// Tier → bar width score
export const TIER_SCORE: Record<string, number> = {
  S: 100, A: 75, B: 50, C: 25, IMPAIRED: 0, DEBT_FREE: 75, UNKNOWN: 50,
};

// Korean labels
export const STAT_LABEL_KO: Record<string, string> = {
  profitability: '수익성',
  growth:        '성장성',
  stability:     '안정성',
  efficiency:    '효율성',
  valuation:     '밸류에이션',
  cash_power:    '현금창출력',
};

export const INDICATOR_LABEL_KO: Record<string, string> = {
  opm:         'OPM',
  roe:         'ROE',
  rev_yoy:     '매출 YoY',
  rev_3y_cagr: '3Y CAGR',
  dr:          '부채비율',
  icr:         '이자보상배율',
  asset_turn:  '자산회전율',
  per:         'PER',
  ev_ebitda:   'EV/EBITDA',
  fcf_margin:  'FCF Margin',
  net_cash:    '순현금',
};

export const SECTOR_ORDER = [
  'IT', '금융', '헬스케어', '경기소비재', '필수소비재',
  '에너지', '산업재', '유틸리티', '소재', '커뮤니케이션', '부동산',
];

// avg_stats 키 기준 방향 (↑ 높을수록 좋음, ↓ 낮을수록 좋음)
export const METRIC_DIRECTION: Record<string, '↑' | '↓'> = {
  opm:        '↑',
  roe:        '↑',
  rev_yoy:    '↑',
  cagr:       '↑',
  dr:         '↓',
  icr:        '↑',
  asset_turn: '↑',
  per:        '↓',
  ev_ebitda:  '↓',
  fcf_margin: '↑',
};
