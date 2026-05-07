import type { ReactNode } from 'react';
import TopBar from './TopBar';
import SideNav from './SideNav';
import DemoBanner from '../common/DemoBanner';
import Disclaimer from '../common/Disclaimer';

interface Props {
  children: ReactNode;
  priceDate?: string | null;
  fiscalYear?: number;
  n?: number;
}

export default function Layout({ children, priceDate, fiscalYear, n }: Props) {
  return (
    <div className="min-h-screen bg-slate-950">
      <TopBar />
      <SideNav />
      <div className="md:ml-16 pt-14 flex flex-col min-h-screen">
        <DemoBanner priceDate={priceDate} />
        <main className="flex-1">{children}</main>
        <Disclaimer priceDate={priceDate} fiscalYear={fiscalYear} n={n} />
      </div>
    </div>
  );
}
