import { KpiCard } from "@/components";
import { PermissionStats } from "@/features/permissions/types/permission";

export function PermissionStatsCards({ stats }: { stats: PermissionStats }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Permissions" value={String(stats.total)} />
      <KpiCard title="Active" value={String(stats.active)} />
      <KpiCard title="Inactive" value={String(stats.inactive)} />
      <KpiCard title="Modules Covered" value={String(stats.modules)} />
    </section>
  );
}
