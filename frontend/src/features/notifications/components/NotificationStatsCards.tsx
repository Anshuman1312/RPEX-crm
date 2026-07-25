import { KpiCard } from "@/components";
import { NotificationStats } from "@/features/notifications/types/notification";

interface NotificationStatsCardsProps {
  stats: NotificationStats;
}

export function NotificationStatsCards({ stats }: NotificationStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Notifications" value={String(stats.total)} />
      <KpiCard title="Unread" value={String(stats.unread)} />
      <KpiCard title="Read" value={String(stats.read)} />
      <KpiCard title="Archived" value={String(stats.archived)} />
    </section>
  );
}
