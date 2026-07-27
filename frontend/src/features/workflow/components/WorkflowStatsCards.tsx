import { KpiCard } from "@/components";
import { WorkflowStats } from "@/features/workflow/types/workflow";

export function WorkflowStatsCards({ stats }: { stats: WorkflowStats }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Workflows" value={String(stats.total)} />
      <KpiCard title="Active" value={String(stats.active)} />
      <KpiCard title="Paused" value={String(stats.paused)} />
      <KpiCard title="Draft" value={String(stats.draft)} />
    </section>
  );
}
