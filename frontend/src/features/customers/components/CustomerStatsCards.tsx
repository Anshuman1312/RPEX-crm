import { KpiCard } from "@/components";
import { CustomerStats } from "@/features/customers/types/customer";

interface CustomerStatsCardsProps {
  stats: CustomerStats;
}

export function CustomerStatsCards({ stats }: CustomerStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Clients" value={String(stats.total)} />
      <KpiCard title="Self Use Intent" value={String(stats.selfUse)} />
      <KpiCard title="Investment Intent" value={String(stats.investment)} />
      <KpiCard title="Business Intent" value={String(stats.business)} />
    </section>
  );
}
