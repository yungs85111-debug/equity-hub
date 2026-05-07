import { TIER_COLOR } from '../config/skills_config';
import type { Tier } from '../types/domain';

export function tierHex(tier: string | null | undefined): string {
  return TIER_COLOR[tier ?? 'UNKNOWN'] ?? TIER_COLOR.UNKNOWN;
}

export function tierBorderClass(tier: Tier | string | null): string {
  const map: Record<string, string> = {
    S: 'border-tier-s', A: 'border-tier-a',
    B: 'border-tier-b', C: 'border-tier-c',
    IMPAIRED: 'border-tier-impaired', UNKNOWN: 'border-tier-unknown',
  };
  return map[tier ?? 'UNKNOWN'] ?? 'border-slate-600';
}
