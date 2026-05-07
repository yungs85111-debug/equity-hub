import { Link, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { label: '섹터 허브', path: '/',        match: (p: string) => p === '/' || p.startsWith('/sector') || p.startsWith('/company') },
  { label: '아카데미',  path: '/academy', match: (p: string) => p === '/academy' },
];

export default function TopBar() {
  const { pathname } = useLocation();

  return (
    <header className="fixed top-0 left-0 right-0 z-40 h-14 bg-slate-950/90 border-b border-slate-800 backdrop-blur-md flex items-center px-6 gap-6">
      <Link to="/" className="flex items-center gap-2 mr-6 shrink-0">
        <span className="text-blue-400 font-black text-xl tracking-tight">EQUITY</span>
        <span className="text-slate-200 font-black text-xl tracking-tight">HUB</span>
      </Link>

      <nav className="hidden md:flex items-center gap-1 flex-1">
        {NAV_ITEMS.map(({ label, path, match }) => (
          <Link
            key={label}
            to={path}
            className={`text-sm px-4 py-2 rounded transition-colors font-medium ${
              match(pathname)
                ? 'text-blue-400 bg-blue-500/10'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {label}
          </Link>
        ))}
      </nav>

      <div className="ml-auto flex items-center gap-2">
        <span className="text-xs text-slate-600 hidden lg:block">뇌동매매 하지 말고, 알고 투자하자</span>
        <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
          <span className="material-symbols-outlined text-blue-400 text-base">person</span>
        </div>
      </div>
    </header>
  );
}
