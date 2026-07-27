import { KpiCard } from "@/components";
import { OrganizationStats } from "@/features/organization/types/organization";

export function OrganizationStatsCards({ stats }: { stats: OrganizationStats }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Organizations" value={String(stats.total)} />
      <KpiCard title="Active" value={String(stats.active)} />
      <KpiCard title="Suspended" value={String(stats.suspended)} />
      <KpiCard title="Inactive" value={String(stats.inactive)} />
    </section>
  );
}
