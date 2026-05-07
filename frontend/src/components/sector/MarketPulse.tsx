import DemoFixedTag from '../common/DemoFixedTag';

const PULSE_DATA = [
  { label: 'VIX',     value: '18.4',  change: '-1.2',  up: false },
  { label: 'US 10Y',  value: '4.32%', change: '+0.05', up: true  },
  { label: 'S&P 500', value: '5,204', change: '+0.3%', up: true  },
  { label: 'USD/KRW', value: '1,338', change: '-2',    up: false },
  { label: 'WTI',     value: '$82.1', change: '+1.2%', up: true  },
];

export default function MarketPulse() {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-slate-300 uppercase tracking-wider">Market Pulse</h3>
        <DemoFixedTag />
      </div>
      <div className="grid grid-cols-3 lg:grid-cols-5 gap-4">
        {PULSE_DATA.map(({ label, value, change, up }) => (
          <div key={label} className="flex flex-col gap-1">
            <span className="text-xs text-slate-500 uppercase tracking-wider">{label}</span>
            <span className="text-base font-bold text-slate-200">{value}</span>
            <span className={`text-sm font-medium ${up ? 'text-emerald-400' : 'text-red-400'}`}>
              {change}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
