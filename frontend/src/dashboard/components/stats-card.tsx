import { ComponentType } from "react";

export interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ComponentType;
  colorClass?: string;
}

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  colorClass = "text-cyan-500",
}: StatCardProps) => (
  <div className="card p-5 flex items-start justify-between group hover:border-cyan-500/50 transition-all cursor-default bg-slate-900 border border-slate-800 rounded-2xl shadow-sm">
    <div>
      <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">
        {title}
      </p>
      <p className="font-display text-2xl mt-2 text-white font-bold">{value}</p>
      {subtitle && (
        <p className="text-slate-400 text-[10px] mt-1 font-medium">
          {subtitle}
        </p>
      )}
    </div>
    <div
      className={`p-3 rounded-xl bg-slate-800/80 ${colorClass} group-hover:scale-110 transition-transform`}
    >
      <Icon />
    </div>
  </div>
);

export default StatCard;
