import { KpiCard } from "@/components";
import { FollowUpStats } from "@/features/followups/types/followup";

interface FollowUpStatsCardsProps {
  stats: FollowUpStats;
}

export function FollowUpStatsCards({ stats }: FollowUpStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Follow-ups" value={String(stats.total)} />
      <KpiCard title="Pending" value={String(stats.pending)} />
      <KpiCard title="Due Today" value={String(stats.dueToday)} />
      <KpiCard title="Completed" value={String(stats.done)} />
    </section>
  );
}
