import { KpiCard } from "@/components";
import { InventoryStats } from "@/features/inventory/types/inventory";

interface InventoryStatsCardsProps {
  stats: InventoryStats;
}

export function InventoryStatsCards({ stats }: InventoryStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Units" value={String(stats.totalUnits)} />
      <KpiCard title="Available" value={String(stats.availableUnits)} />
      <KpiCard title="Reserved" value={String(stats.reservedUnits)} />
      <KpiCard title="Sold" value={String(stats.soldUnits)} />
    </section>
  );
}
