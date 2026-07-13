import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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
    }
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

  return (
    <div className="p-6 space-y-6">
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

      <section className="card p-6">
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
      </section>
    </div>
  );
}
