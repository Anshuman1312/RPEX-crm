import { KpiCard } from "@/components";
import { LeadStats } from "@/features/leads/types/lead";

interface LeadStatsCardsProps {
  stats: LeadStats;
}

export function LeadStatsCards({ stats }: LeadStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Leads" value={String(stats.total)} />
      <KpiCard title="New Leads" value={String(stats.newLeads)} />
      <KpiCard title="Qualified" value={String(stats.qualified)} />
      <KpiCard title="Won" value={String(stats.won)} />
    </section>
  );
}
