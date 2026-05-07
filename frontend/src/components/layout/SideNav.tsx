import { Link, useLocation } from 'react-router-dom';

const MENU = [
  { icon: 'grid_view', label: '섹터 허브', path: '/',        match: (p: string) => p === '/' || p.startsWith('/sector') || p.startsWith('/company') },
  { icon: 'school',    label: '아카데미',  path: '/academy', match: (p: string) => p === '/academy' },
];

export default function SideNav() {
  const { pathname } = useLocation();

  return (
    <aside className="fixed left-0 top-14 bottom-0 w-16 bg-slate-950 border-r border-slate-800 z-30 flex flex-col items-center py-4 gap-1 hidden md:flex">
      {MENU.map(({ icon, label, path, match }) => (
        <Link
          key={label}
          to={path}
          className={`flex flex-col items-center gap-1 p-2 rounded transition-colors w-full ${
            match(pathname)
              ? 'text-blue-400 bg-blue-500/10 border-r-2 border-blue-500'
              : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800'
          }`}
          title={label}
        >
          <span className="material-symbols-outlined text-2xl">{icon}</span>
          <span className="text-[10px] text-center leading-tight">{label}</span>
        </Link>
      ))}
    </aside>
  );
}
