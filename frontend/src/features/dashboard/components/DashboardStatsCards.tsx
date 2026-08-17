import {
  Users,
  TrendingUp,
  Target,
  Megaphone,
  CalendarCheck,
  FolderKanban,
  AlertCircle,
  CheckCircle2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components";
import { useGetDashboardKpisQuery } from "@/features/dashboard/services/dashboardApi";

interface StatTileProps {
  label: string;
  value: number;
  sub?: string;
  accent?: "blue" | "green" | "yellow" | "red" | "purple" | "indigo";
}

const accentClasses: Record<NonNullable<StatTileProps["accent"]>, string> = {
  blue:   "bg-blue-500/10 text-blue-500",
  green:  "bg-emerald-500/10 text-emerald-500",
  yellow: "bg-yellow-500/10 text-yellow-500",
  red:    "bg-rose-500/10 text-rose-500",
  purple: "bg-purple-500/10 text-purple-500",
  indigo: "bg-indigo-500/10 text-indigo-500"
};

function StatTile({ label, value, sub, accent = "blue" }: StatTileProps) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border bg-card p-3">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`text-xl font-bold ${accentClasses[accent].split(" ")[1]}`}>
        {value.toLocaleString()}
      </span>
      {sub ? <span className="text-xs text-muted-foreground">{sub}</span> : null}
    </div>
  );
}

interface SectionCardProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

function SectionCard({ title, icon, children }: SectionCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
        <span className="text-primary">{icon}</span>
        <CardTitle className="text-sm font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-2 p-4 pt-0">
        {children}
      </CardContent>
    </Card>
  );
}

export function DashboardStatsCards() {
  const { data, isLoading, isError } = useGetDashboardKpisQuery();

  if (isLoading) {
    return <LoadingState label="Loading stats..." />;
  }

  if (isError || !data) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
        Could not load live stats. Showing cached data below.
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
      {/* Leads */}
      <SectionCard title="Leads" icon={<Target className="h-4 w-4" />}>
        <StatTile label="Total" value={data.leads.total_leads} accent="blue" />
        <StatTile label="New" value={data.leads.new_leads} accent="indigo" />
        <StatTile label="Qualified" value={data.leads.qualified_leads} accent="green" />
        <StatTile label="Warm" value={data.leads.warm_leads} accent="yellow" />
      </SectionCard>

      {/* Campaigns */}
      <SectionCard title="Campaigns" icon={<Megaphone className="h-4 w-4" />}>
        <StatTile label="Total" value={data.campaigns.total_campaigns} accent="purple" />
        <StatTile label="Active" value={data.campaigns.active_campaigns} accent="green" />
        <StatTile label="Upcoming" value={data.campaigns.upcoming_campaigns} accent="yellow" />
        <StatTile label="Ended" value={data.campaigns.ended_campaigns} accent="red" />
      </SectionCard>

      {/* Customers */}
      <SectionCard title="Customers" icon={<Users className="h-4 w-4" />}>
        <StatTile label="Total" value={data.customers.total_customers} accent="blue" />
        <StatTile label="Active" value={data.customers.active_customers} accent="green" />
        <StatTile label="Inactive" value={data.customers.inactive_customers} accent="yellow" />
        <StatTile label="Blacklisted" value={data.customers.blacklisted_customers} accent="red" />
      </SectionCard>

      {/* Follow-ups */}
      <SectionCard title="Follow-ups" icon={<CalendarCheck className="h-4 w-4" />}>
        <StatTile label="Total" value={data.followups.total_followups} accent="indigo" />
        <StatTile label="Scheduled" value={data.followups.scheduled_followups} accent="blue" />
        <StatTile label="Completed" value={data.followups.completed_followups} accent="green" />
        <StatTile label="Overdue" value={data.followups.overdue_followups} accent="red" sub="action needed" />
      </SectionCard>

      {/* Projects */}
      <SectionCard title="Projects" icon={<FolderKanban className="h-4 w-4" />}>
        <StatTile label="Total" value={data.projects.total_projects} accent="purple" />
        <StatTile label="Planning" value={data.projects.planning_projects} accent="yellow" />
        <StatTile label="Ongoing" value={data.projects.ongoing_projects} accent="blue" />
        <StatTile label="Completed" value={data.projects.completed_projects} accent="green" />
      </SectionCard>
    </div>
  );
}
