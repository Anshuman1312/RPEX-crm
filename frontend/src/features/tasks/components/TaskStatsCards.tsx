import { KpiCard } from "@/components";
import { TaskStats } from "@/features/tasks/types/task";

interface TaskStatsCardsProps {
  stats: TaskStats;
}

export function TaskStatsCards({ stats }: TaskStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Tasks" value={String(stats.total)} />
      <KpiCard title="In Progress" value={String(stats.inProgress)} />
      <KpiCard title="Blocked" value={String(stats.blocked)} />
      <KpiCard title="Completed" value={String(stats.completed)} />
    </section>
  );
}
