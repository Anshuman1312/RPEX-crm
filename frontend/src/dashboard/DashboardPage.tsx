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
  today_leads: number;
  converted_leads: number;
  pending_leads: number;
  conversion_rate: number;
  top_campaign: string | null;
  top_keyword: string | null;
};

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

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h1 className="font-display text-3xl text-ink">Operations Dashboard</h1>
        <p className="text-steel mt-2">Real-time visibility for lead flow, campaign health, and conversion momentum.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Total Leads", data?.total_leads ?? 0],
          ["Today's Leads", data?.today_leads ?? 0],
          ["Converted", data?.converted_leads ?? 0],
          ["Conversion %", data?.conversion_rate ?? 0]
        ].map(([label, value]) => (
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
        <div className="h-72">
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
          <div className="h-72 mt-3">
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
        <div className="h-64">
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
    </div>
  );
}
