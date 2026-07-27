import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";
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
import { DashboardWidgetId, QuickActionItem } from "@/features/dashboard/types";
import { PageContainer } from "@/layouts/components/PageContainer";

const widgetLabels: Array<{ id: DashboardWidgetId; label: string }> = [
  { id: "leadStats", label: "Lead Stats" },
  { id: "revenueTrend", label: "Revenue Trend" },
  { id: "bookingPipeline", label: "Booking Pipeline" },
  { id: "payments", label: "Payments" },
  { id: "tasks", label: "Tasks" },
  { id: "meetings", label: "Meetings" },
  { id: "recentActivity", label: "Recent Activity" },
  { id: "quickActions", label: "Quick Actions" }
];

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

      {isWidgetVisible("leadStats") ? (
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {data.kpis.map(metric => (
            <KpiCard
              change={metric.change}
              key={metric.id}
              positive={metric.positive}
              title={metric.label}
              value={metric.value}
            />
          ))}
        </section>
      ) : null}

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
        {isWidgetVisible("tasks") ? <TaskSummaryCard items={data.tasks} /> : null}
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {isWidgetVisible("meetings") ? <MeetingsCard items={data.meetings} /> : null}
        {isWidgetVisible("recentActivity") ? <RecentActivityCard items={data.recentActivity} /> : null}
      </section>

      {isWidgetVisible("quickActions") ? (
        <QuickActionsCard items={data.quickActions} onActionClick={handleQuickAction} />
      ) : null}
    </PageContainer>
  );
}
