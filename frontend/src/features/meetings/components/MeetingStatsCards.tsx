import { KpiCard } from "@/components";
import { MeetingStats } from "@/features/meetings/types/meeting";

interface MeetingStatsCardsProps {
  stats: MeetingStats;
}

export function MeetingStatsCards({ stats }: MeetingStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Meetings" value={String(stats.total)} />
      <KpiCard title="Scheduled" value={String(stats.scheduled)} />
      <KpiCard title="Completed" value={String(stats.completed)} />
      <KpiCard title="Cancelled" value={String(stats.cancelled)} />
    </section>
  );
}
