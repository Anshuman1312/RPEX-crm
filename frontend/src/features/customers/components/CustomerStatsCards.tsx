import { KpiCard } from "@/components";
import { CustomerStats } from "@/features/customers/types/customer";

interface CustomerStatsCardsProps {
  stats: CustomerStats;
}

export function CustomerStatsCards({ stats }: CustomerStatsCardsProps) {
  const activeCount = stats.by_status?.active ?? stats.by_status?.ACTIVE ?? 0;
  const individualCount = stats.by_type?.individual ?? stats.by_type?.INDIVIDUAL ?? 0;
  const corporateCount = stats.by_type?.corporate ?? stats.by_type?.CORPORATE ?? 0;

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Clients" value={String(stats.total ?? 0)} />
      <KpiCard title="Active Clients" value={String(activeCount)} />
      <KpiCard title="Individual Clients" value={String(individualCount)} />
      <KpiCard title="Corporate Clients" value={String(corporateCount)} />
    </section>
  );
}
