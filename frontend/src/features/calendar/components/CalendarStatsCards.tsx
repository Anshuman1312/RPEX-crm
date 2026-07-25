import { KpiCard } from "@/components";
import { CalendarStats } from "@/features/calendar/types/calendar";

interface CalendarStatsCardsProps {
  stats: CalendarStats;
}

export function CalendarStatsCards({ stats }: CalendarStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Events" value={String(stats.total)} />
      <KpiCard title="Upcoming" value={String(stats.upcoming)} />
      <KpiCard title="Completed" value={String(stats.completed)} />
      <KpiCard title="Missed" value={String(stats.missed)} />
    </section>
  );
}
