import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";
import {
  AlertTriangle,
  Archive,
  BookOpen,
  Building2,
  CalendarCheck,
  Eye,
  FolderKanban,
  Hourglass,
  LayoutList,
  Megaphone,
  TrendingUp,
  Users,
  CheckCircle2,
  Clock,
  XCircle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, ErrorState, KpiCard, LineTrendChart, LoadingState } from "@/components";
import {
  DashboardWidgetVisibility,
  MeetingsCard,
  PaymentBreakdownChart,
  QuickActionsCard,
  RecentActivityCard,
  TaskSummaryCard
} from "@/features/dashboard/components";
import { useDashboardOverview, useDashboardPreferences } from "@/features/dashboard/hooks";
import { useGetDashboardKpisQuery, useGetDashboardLeadKpisQuery } from "@/features/dashboard/services/dashboardApi";
import { DashboardWidgetId, QuickActionItem } from "@/features/dashboard/types";
import { PageContainer } from "@/layouts/components/PageContainer";

const widgetLabels: Array<{ id: DashboardWidgetId; label: string }> = [
  { id: "leadStats",       label: "Lead Pipeline KPIs" },
  { id: "customers",       label: "Customers" },
  { id: "campaigns",       label: "Campaigns" },
  { id: "followups",       label: "Follow-ups" },
  { id: "projects",        label: "Projects" },
  { id: "revenueTrend",    label: "Revenue Trend" },
  { id: "bookingPipeline", label: "Booking Pipeline" },
  { id: "payments",        label: "Payments" },
  { id: "tasks",           label: "Tasks" },
  { id: "meetings",        label: "Meetings" },
  { id: "recentActivity",  label: "Recent Activity" },
  { id: "quickActions",    label: "Quick Actions" }
];

// ── Lead Pipeline Widget ───────────────────────────────────────────────

function LeadPipelineKpiCards() {
  const { data, isLoading, isFetching } = useGetDashboardLeadKpisQuery();

  if (isLoading || isFetching || !data) {
    return (
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div className="h-24 animate-pulse rounded-lg border bg-muted/40" key={i} />
        ))}
      </section>
    );
  }

  const kpis = [
    { id: "total_leads",  label: "Total Leads",              value: data.total_leads,     icon: LayoutList,    positive: true },
    { id: "open_leads",   label: "Total Open Leads",         value: data.open_leads,      icon: TrendingUp,    positive: true },
    { id: "follow",       label: "Follow-up Leads",          value: data.follow_leads,    icon: Hourglass,     positive: data.follow_leads === 0 },
    { id: "visit",        label: "Visit Scheduled",          value: data.visit_scheduled, icon: Eye,           positive: true },
    { id: "visited",      label: "Total Visited Leads",      value: data.visited_leads,   icon: Users,         positive: true },
    { id: "booking",      label: "Total Booking Leads",      value: data.booking_leads,   icon: BookOpen,      positive: true },
    { id: "lost",         label: "Future Perspective Leads", value: data.lost_leads,      icon: AlertTriangle, positive: false },
    { id: "inactive",     label: "Inactive / Duplicate",     value: data.inactive_leads,  icon: Archive,       positive: false },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {kpis.map(metric => (
        <KpiCard
          icon={metric.icon}
          key={metric.id}
          positive={metric.positive}
          title={metric.label}
          value={metric.value.toLocaleString()}
        />
      ))}
    </section>
  );
}

// ── Shared KPI Section Card ────────────────────────────────────────────

interface DomainSectionProps {
  title: string;
  icon: React.ReactNode;
  kpis: Array<{ id: string; label: string; value: number; icon: React.ElementType; positive?: boolean }>;
  isLoading: boolean;
}

function DomainKpiSection({ title, icon, kpis, isLoading }: DomainSectionProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
          <span className="text-primary">{icon}</span>
          <CardTitle className="text-sm font-semibold">{title}</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 p-4 pt-0 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div className="h-16 animate-pulse rounded-lg bg-muted/50" key={i} />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
        <span className="text-primary">{icon}</span>
        <CardTitle className="text-sm font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-3 p-4 pt-0 xl:grid-cols-4">
        {kpis.map(metric => {
          const Icon = metric.icon;
          return (
            <div
              className="flex flex-col gap-1.5 rounded-lg bg-muted/40 px-3 py-2.5"
              key={metric.id}
            >
              <div className="flex items-center gap-1.5">
                <Icon className="h-3.5 w-3.5 text-muted-foreground/60" />
                <span className="text-xs text-muted-foreground">{metric.label}</span>
              </div>
              <span
                className={`text-xl font-bold ${
                  (metric.positive ?? true) ? "text-foreground" : "text-rose-500"
                }`}
              >
                {metric.value.toLocaleString()}
              </span>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

// ── Domain Widgets ─────────────────────────────────────────────────────

function CustomersWidget() {
  const { data, isLoading } = useGetDashboardKpisQuery();
  return (
    <DomainKpiSection
      icon={<Users className="h-4 w-4" />}
      isLoading={isLoading || !data}
      kpis={[
        { id: "total",       label: "Total",       value: data?.customers.total_customers       ?? 0, icon: Users,        positive: true },
        { id: "active",      label: "Active",      value: data?.customers.active_customers      ?? 0, icon: CheckCircle2, positive: true },
        { id: "inactive",    label: "Inactive",    value: data?.customers.inactive_customers    ?? 0, icon: Clock,        positive: false },
        { id: "blacklisted", label: "Blacklisted", value: data?.customers.blacklisted_customers ?? 0, icon: XCircle,      positive: false },
      ]}
      title="Customers"
    />
  );
}

function CampaignsWidget() {
  const { data, isLoading } = useGetDashboardKpisQuery();
  return (
    <DomainKpiSection
      icon={<Megaphone className="h-4 w-4" />}
      isLoading={isLoading || !data}
      kpis={[
        { id: "total",    label: "Total",    value: data?.campaigns.total_campaigns    ?? 0, icon: Megaphone,  positive: true },
        { id: "active",   label: "Active",   value: data?.campaigns.active_campaigns   ?? 0, icon: TrendingUp, positive: true },
        { id: "upcoming", label: "Upcoming", value: data?.campaigns.upcoming_campaigns ?? 0, icon: CalendarCheck, positive: true },
        { id: "ended",    label: "Ended",    value: data?.campaigns.ended_campaigns    ?? 0, icon: Archive,    positive: false },
      ]}
      title="Campaigns"
    />
  );
}

function FollowupsWidget() {
  const { data, isLoading } = useGetDashboardKpisQuery();
  return (
    <DomainKpiSection
      icon={<CalendarCheck className="h-4 w-4" />}
      isLoading={isLoading || !data}
      kpis={[
        { id: "total",     label: "Total",     value: data?.followups.total_followups     ?? 0, icon: LayoutList,   positive: true },
        { id: "scheduled", label: "Scheduled", value: data?.followups.scheduled_followups ?? 0, icon: Clock,        positive: true },
        { id: "completed", label: "Completed", value: data?.followups.completed_followups ?? 0, icon: CheckCircle2, positive: true },
        { id: "overdue",   label: "Overdue",   value: data?.followups.overdue_followups   ?? 0, icon: AlertTriangle, positive: false },
      ]}
      title="Follow-ups"
    />
  );
}

function ProjectsWidget() {
  const { data, isLoading } = useGetDashboardKpisQuery();
  return (
    <DomainKpiSection
      icon={<FolderKanban className="h-4 w-4" />}
      isLoading={isLoading || !data}
      kpis={[
        { id: "total",     label: "Total",     value: data?.projects.total_projects     ?? 0, icon: Building2,    positive: true },
        { id: "planning",  label: "Planning",  value: data?.projects.planning_projects  ?? 0, icon: Hourglass,    positive: true },
        { id: "ongoing",   label: "Ongoing",   value: data?.projects.ongoing_projects   ?? 0, icon: TrendingUp,   positive: true },
        { id: "completed", label: "Completed", value: data?.projects.completed_projects ?? 0, icon: CheckCircle2, positive: true },
      ]}
      title="Projects"
    />
  );
}

// ── Main Page ──────────────────────────────────────────────────────────

export function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboardOverview();
  const { isWidgetVisible, toggleWidget } = useDashboardPreferences();

  const handleQuickAction = (item: QuickActionItem) => {
    toast.success(`${item.label} action is ready for integration.`);
  };

  if (isLoading) {
    return <LoadingState label="Loading dashboard overview..." />;
  }

  if (isError || !data) {
    return <ErrorState description="Dashboard data could not be loaded." onRetry={() => void refetch()} />;
  }

  return (
    <PageContainer
      description="Configurable KPI dashboard across leads, revenue, bookings, payments, tasks, and meetings."
      title="Dashboard"
    >
      <DashboardWidgetVisibility
        isVisible={isWidgetVisible}
        onToggle={toggleWidget}
        widgets={widgetLabels}
      />

      {/* Lead Pipeline KPIs */}
      {isWidgetVisible("leadStats") ? <LeadPipelineKpiCards /> : null}

      {/* Domain stats widgets */}
      <div className="grid gap-4 xl:grid-cols-2">
        {isWidgetVisible("customers") ? <CustomersWidget /> : null}
        {isWidgetVisible("campaigns") ? <CampaignsWidget /> : null}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {isWidgetVisible("followups") ? <FollowupsWidget /> : null}
        {isWidgetVisible("projects")  ? <ProjectsWidget />  : null}
      </div>

      {/* Charts */}
      <section className="grid gap-4 xl:grid-cols-2">
        {isWidgetVisible("revenueTrend") ? (
          <LineTrendChart data={data.leadTrend} title="Lead Growth Trend" />
        ) : null}

        {isWidgetVisible("bookingPipeline") ? (
          <Card>
            <CardHeader className="p-4 pb-3">
              <CardTitle className="text-sm font-semibold">Booking Pipeline</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0 h-64 w-full">
              <ResponsiveContainer>
                <BarChart data={data.bookingPipeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                  <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        ) : null}
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {isWidgetVisible("payments") ? <PaymentBreakdownChart data={data.paymentBreakdown} /> : null}
        {isWidgetVisible("tasks")    ? <TaskSummaryCard items={data.tasks} />                 : null}
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {isWidgetVisible("meetings")       ? <MeetingsCard items={data.meetings} />             : null}
        {isWidgetVisible("recentActivity") ? <RecentActivityCard items={data.recentActivity} /> : null}
      </section>

      {isWidgetVisible("quickActions") ? (
        <QuickActionsCard items={data.quickActions} onActionClick={handleQuickAction} />
      ) : null}
    </PageContainer>
  );
}
