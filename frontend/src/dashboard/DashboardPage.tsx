import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { api } from "../services/api";

type DashboardMetrics = {
  total_leads: number;
  new_leads_today: number;
  site_visits_today: number;
  bookings: number;
  sales_value: number;
  revenue: number;
  marketing_spend: number;
  cpl: number;
  pending_followups: number;
  today_leads: number;
  converted_leads: number;
  pending_leads: number;
  conversion_rate: number;
  top_campaign: string | null;
  top_keyword: string | null;
  sales_team_performance: Array<{
    user_id: string;
    name: string;
    assigned_leads: number;
    converted_leads: number;
    bookings: number;
    sales_value: number;
    conversion_rate: number;
  }>;
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(value || 0);
}

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["dashboard-metrics"],
    queryFn: async () => {
      const response = await api.get<DashboardMetrics>("/analytics/dashboard");
      return response.data;
    },
    refetchInterval: 15000
  });

  const chartData = useMemo(
    () => [
      { name: "Total", value: data?.total_leads ?? 0 },
      { name: "Today", value: data?.today_leads ?? 0 },
      { name: "Converted", value: data?.converted_leads ?? 0 },
      { name: "Pending", value: data?.pending_leads ?? 0 }
    ],
    [data]
  );

  const splitData = useMemo(
    () => [
      { name: "Converted", value: data?.converted_leads ?? 0 },
      { name: "Pending", value: data?.pending_leads ?? 0 }
    ],
    [data]
  );

  const performanceData = useMemo(
    () => (data?.sales_team_performance ?? []).slice(0, 8).map((row) => ({
      name: row.name,
      sales_value: Number(row.sales_value ?? 0),
      conversion_rate: Number(row.conversion_rate ?? 0)
    })),
    [data]
  );

  const metricCards: Array<[string, string | number]> = [
    ["Total Leads", data?.total_leads ?? 0],
    ["New Leads Today", data?.new_leads_today ?? 0],
    ["Site Visits Today", data?.site_visits_today ?? 0],
    ["Bookings", data?.bookings ?? 0],
    ["Sales Value", formatCurrency(data?.sales_value ?? 0)],
    ["Revenue", formatCurrency(data?.revenue ?? 0)],
    ["Marketing Spend", formatCurrency(data?.marketing_spend ?? 0)],
    ["Cost Per Lead (CPL)", formatCurrency(data?.cpl ?? 0)],
    ["Conversion Rate", `${data?.conversion_rate ?? 0}%`],
    ["Pending Follow-ups", data?.pending_followups ?? 0]
  ];

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h1 className="font-display text-3xl text-ink">Operations Dashboard</h1>
        <p className="text-steel mt-2">Real-time visibility for lead flow, campaign health, and conversion momentum.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {metricCards.map(([label, value]) => (
          <article key={String(label)} className="card p-5">
            <p className="text-steel text-sm">{label}</p>
            <p className="font-display text-3xl mt-2 text-ink">{value}</p>
          </article>
        ))}
      </div>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="card p-6 xl:col-span-2">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 className="font-display text-2xl text-ink">Lead Velocity</h2>
          <div className="text-sm text-steel">
            Top campaign: <span className="font-semibold text-ink">{data?.top_campaign ?? "N/A"}</span>
          </div>
        </div>
        <div className="h-64 sm:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#0ea5a4" fill="#99f6e4" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        </div>

        <div className="card p-6">
          <h2 className="font-display text-2xl text-ink">Conversion Split</h2>
          <div className="h-64 sm:h-72 mt-3">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={splitData} dataKey="value" nameKey="name" outerRadius={95} fill="#0ea5a4" label />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 className="font-display text-2xl text-ink">Pipeline Compare</h2>
          <div className="text-sm text-steel">
            Top keyword: <span className="font-semibold text-ink">{data?.top_keyword ?? "N/A"}</span>
          </div>
        </div>
        <div className="h-56 sm:h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#f59e0b" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="card p-6 xl:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <h2 className="font-display text-2xl text-ink">Sales Team Performance</h2>
            <p className="text-sm text-steel">Ranked by sales value and conversions</p>
          </div>
          <div className="h-64 sm:h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="sales_value" fill="#0ea5a4" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="font-display text-2xl text-ink">Top Contributors</h2>
          <div className="mt-4 space-y-3 text-sm">
            {(data?.sales_team_performance ?? []).slice(0, 6).map((row) => (
              <div key={row.user_id} className="rounded-xl border border-slate-100 p-3">
                <p className="font-semibold text-ink">{row.name}</p>
                <p className="text-steel">Assigned: {row.assigned_leads} | Converted: {row.converted_leads}</p>
                <p className="text-steel">Bookings: {row.bookings} | Sales: {formatCurrency(row.sales_value)}</p>
              </div>
            ))}
            {(data?.sales_team_performance ?? []).length === 0 ? <p className="text-steel">No team performance data yet.</p> : null}
          </div>
        </div>
      </section>
    </div>
  );
}
