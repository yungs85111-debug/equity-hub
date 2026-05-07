interface Props { message?: string; onRetry?: () => void; }

export default function ErrorState({ message = '데이터를 불러오는 데 실패했습니다.', onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center p-16 text-slate-500 gap-4">
      <span className="material-symbols-outlined text-4xl text-red-500/50">error</span>
      <p className="text-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs border border-slate-700 px-4 py-1.5 rounded hover:bg-slate-800"
        >
          재시도
        </button>
      )}
    </div>
  );
}
