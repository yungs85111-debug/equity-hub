import { useApi } from '../hooks/useApi';
import type { SectorsResponse } from '../types';
import Layout from '../components/layout/Layout';
import SectorCard from '../components/sector/SectorCard';
import MarketPulse from '../components/sector/MarketPulse';
import LoadingSkeleton from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';

export default function SectorHub() {
  const { data, loading, error, refetch } = useApi<SectorsResponse>('/sectors');

  if (loading) return <Layout><LoadingSkeleton lines={12} /></Layout>;
  if (error || !data) return <Layout><ErrorState message={error?.message} onRetry={refetch} /></Layout>;

  return (
    <Layout priceDate={data.price_date} fiscalYear={data.fiscal_year}>
      <div className="px-6 py-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-xl font-black text-slate-100 tracking-tight">SECTOR HUB</h1>
          <p className="text-xs text-slate-500 mt-1">
            S&amp;P 500 / NASDAQ 100 기준 11개 GICS 섹터 분석 | {data.fiscal_year}년 10-K
          </p>
        </div>

        {/* 3×4 섹터 카드 그리드 (sector_hub.html §5.2 배치 기준) */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-6">
          {data.sectors.map(sector => (
            <SectorCard key={sector.sector} data={sector} />
          ))}
        </div>

        {/* Market Pulse */}
        <MarketPulse />
      </div>
    </Layout>
  );
}
