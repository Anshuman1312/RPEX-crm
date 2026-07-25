import { KpiCard } from "@/components";
import { ActivityStats } from "@/features/activity-timeline/types/activity";

export function ActivityStatsCards({ stats }: { stats: ActivityStats }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Events" value={String(stats.total)} />
      <KpiCard title="Today" value={String(stats.today)} />
      <KpiCard title="Unique Actors" value={String(stats.uniqueActors)} />
      <KpiCard title="Modules Covered" value={String(stats.modules)} />
    </section>
  );
}
