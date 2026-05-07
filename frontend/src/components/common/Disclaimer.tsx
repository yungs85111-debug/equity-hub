// §11 면책 표시 — 모든 화면 하단 필수
interface Props { fiscalYear?: number; priceDate?: string | null; n?: number; }

export default function Disclaimer({ fiscalYear = 2023, priceDate, n }: Props) {
  return (
    <footer className="py-8 px-6 border-t border-slate-800 bg-slate-950/50">
      <p className="text-sm text-slate-500 leading-relaxed max-w-4xl">
        <span className="font-bold text-slate-400">⚠️ DISCLAIMER:</span>{' '}
        본 대시보드는 교육 목적으로 제작되었습니다.
        투자 추천·매수·매도 의견이 아닙니다.
        재무 데이터 출처: SEC EDGAR (data.sec.gov)
        | 데이터 기준: {fiscalYear}년 연간 보고서 (10-K)
        | 주가 기준일: {priceDate ?? '—'}
        {n != null && <> | 벤치마크 출처: demo.db 실측 분위수 ({n}개사, {fiscalYear}년 기준)</>}
        | 본 서비스는 데모 버전으로 실시간 데이터를 제공하지 않습니다.
        실제 투자 전 반드시 전문가 상담을 권장합니다.
      </p>
    </footer>
  );
}
