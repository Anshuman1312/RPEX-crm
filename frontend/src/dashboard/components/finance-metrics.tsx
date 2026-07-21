export interface FinanceMetricsProps {
  targetRevenue: string;
  targetAchievedPercent: number;
  totalOutstanding: string;
  pendingInstallmentsCount: number;
  siteVisitsMonthCount: number;
  visitorsAttendedPercent: number;
}

export const FinanceMetrics = ({
  targetRevenue,
  targetAchievedPercent,
  totalOutstanding,
  pendingInstallmentsCount,
  siteVisitsMonthCount,
  visitorsAttendedPercent,
}: FinanceMetricsProps) => (
  <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Target Revenue Card */}
    <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-3xl p-7 text-white shadow-lg shadow-indigo-100 relative overflow-hidden">
      <div className="relative z-10">
        <p className="text-xs font-bold opacity-70 uppercase tracking-widest mb-1">
          Project Target Revenue
        </p>
        <h2 className="text-4xl font-bold tracking-tight">{targetRevenue}</h2>
        <div className="mt-6 flex items-center justify-between">
          <div className="text-[10px] font-bold py-1 px-2 bg-white/20 rounded-lg">
            Target Status
          </div>
          <span className="text-sm font-bold text-emerald-300">
            {targetAchievedPercent}% Achieved
          </span>
        </div>
        <div className="mt-3 h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-400"
            style={{ width: `${targetAchievedPercent}%` }}
          />
        </div>
      </div>
      {/* Decorator Circle */}
      <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
    </div>

    {/* Total Outstanding Card */}
    <div className="bg-white border border-slate-100 rounded-3xl p-7 shadow-sm">
      <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">
        Total Outstanding
      </p>
      <h2 className="text-3xl font-bold text-rose-500 tracking-tight">
        {totalOutstanding}
      </h2>
      <div className="mt-6 flex items-center justify-between text-xs font-bold">
        <span className="text-slate-500">
          {pendingInstallmentsCount} Pending Installments
        </span>
        <button className="text-cyan-600 hover:text-cyan-700 bg-cyan-50 px-3 py-1.5 rounded-xl transition-colors">
          Send Reminders
        </button>
      </div>
    </div>

    {/* Site Visits Card */}
    <div className="bg-white border border-slate-100 rounded-3xl p-7 shadow-sm">
      <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">
        Site Visits (Month)
      </p>
      <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
        {siteVisitsMonthCount}
      </h2>
      <div className="mt-6">
        <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-2">
          <span>VISITORS ATTENDED</span>
          <span>{visitorsAttendedPercent}%</span>
        </div>
        <div className="h-2 bg-slate-50 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500"
            style={{ width: `${visitorsAttendedPercent}%` }}
          />
        </div>
      </div>
    </div>
  </section>
);

export default FinanceMetrics;
