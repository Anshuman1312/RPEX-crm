import { KpiCard } from "@/components";
import { BookingStats } from "@/features/bookings/types/booking";

interface BookingStatsCardsProps {
  stats: BookingStats;
}

export function BookingStatsCards({ stats }: BookingStatsCardsProps) {
  const formattedTotalAmount = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(stats.totalAmount);

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Bookings" value={String(stats.total)} />
      <KpiCard title="Total Booking Amount" value={formattedTotalAmount} />
      <KpiCard title="Finance Required" value={String(stats.financeRequired)} />
      <KpiCard title="Loan Assistance Required" value={String(stats.loanAssistanceRequired)} />
    </section>
  );
}
