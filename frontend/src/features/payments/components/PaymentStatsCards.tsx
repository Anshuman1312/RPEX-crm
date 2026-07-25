import { KpiCard } from "@/components";
import { PaymentStats } from "@/features/payments/types/payment";

interface PaymentStatsCardsProps {
  stats: PaymentStats;
}

export function PaymentStatsCards({ stats }: PaymentStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Transactions" value={String(stats.totalTransactions)} />
      <KpiCard title="Received" value={String(stats.receivedCount)} />
      <KpiCard title="Pending" value={String(stats.pendingCount)} />
      <KpiCard
        title="Received Amount"
        value={new Intl.NumberFormat("en-IN", {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: 0
        }).format(stats.totalReceivedAmount)}
      />
    </section>
  );
}
