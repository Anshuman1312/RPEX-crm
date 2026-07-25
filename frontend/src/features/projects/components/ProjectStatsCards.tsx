import { KpiCard } from "@/components";
import { ProjectStats } from "@/features/projects/types/project";

interface ProjectStatsCardsProps {
  stats: ProjectStats;
}

export function ProjectStatsCards({ stats }: ProjectStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Projects" value={String(stats.total)} />
      <KpiCard title="On Track" value={String(stats.onTrack)} />
      <KpiCard title="Delayed" value={String(stats.delayed)} />
      <KpiCard title="Near Handover" value={String(stats.nearHandover)} />
    </section>
  );
}
