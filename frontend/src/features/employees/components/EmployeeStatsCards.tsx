import { KpiCard } from "@/components";
import { EmployeeStats } from "@/features/employees/types/employee";

interface EmployeeStatsCardsProps {
  stats: EmployeeStats;
}

export function EmployeeStatsCards({ stats }: EmployeeStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Employees" value={String(stats.total)} />
      <KpiCard title="Active" value={String(stats.active)} />
      <KpiCard title="On Leave" value={String(stats.onLeave)} />
      <KpiCard title="Inactive" value={String(stats.inactive)} />
    </section>
  );
}
