import { KpiCard } from "@/components";
import { CampaignStats } from "@/features/campaigns/types/campaign";

interface CampaignStatsCardsProps {
  stats: CampaignStats;
}

export function CampaignStatsCards({ stats }: CampaignStatsCardsProps) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard title="Total Campaigns" value={String(stats.total)} />
      <KpiCard title="Running" value={String(stats.running)} />
      <KpiCard title="Completed" value={String(stats.completed)} />
      <KpiCard title="Leads Generated" value={String(stats.leadsGenerated)} />
    </section>
  );
}
