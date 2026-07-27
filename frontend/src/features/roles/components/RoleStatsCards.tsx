import { KpiCard } from "@/components";
import { RoleStats } from "@/features/roles/types/role";

export function RoleStatsCards({ stats }: { stats: RoleStats }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Roles" value={String(stats.total)} />
      <KpiCard title="Active" value={String(stats.active)} />
      <KpiCard title="System Roles" value={String(stats.system)} />
      <KpiCard title="Inactive" value={String(stats.inactive)} />
    </section>
  );
}
