import { Link } from 'react-router-dom';
import Layout from '../components/layout/Layout';

export default function NotFound() {
  return (
    <Layout>
      <div className="flex flex-col items-center justify-center h-64 gap-4 text-slate-500">
        <span className="material-symbols-outlined text-5xl text-slate-700">search_off</span>
        <h2 className="text-lg font-bold">페이지를 찾을 수 없습니다</h2>
        <Link to="/" className="text-xs text-blue-400 hover:underline">홈으로 돌아가기</Link>
      </div>
    </Layout>
  );
}
