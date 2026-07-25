import { KpiCard } from "@/components";
import { ReportStats } from "@/features/reports/types/report";

interface ReportStatsCardsProps {
  stats: ReportStats;
}

export function ReportStatsCards({ stats }: ReportStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Reports" value={String(stats.total)} />
      <KpiCard title="Ready" value={String(stats.ready)} />
      <KpiCard title="Exported" value={String(stats.exported)} />
      <KpiCard title="Failed" value={String(stats.failed)} />
    </section>
  );
}
