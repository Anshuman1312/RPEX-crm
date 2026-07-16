import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createSalesTeamReport, fetchSalesTeamLeaderboard, fetchSalesTeamReports } from "../services/crm";

const ATTENDANCE = ["PRESENT", "ABSENT", "LEAVE"] as const;

export default function SalesTeamPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    report_date: "",
    sales_executive_id: "",
    sales_executive_name: "",
    target_value: 0,
    achieved_sales_value: 0,
    bookings_count: 0,
    commission_value: 0,
    site_visits_count: 0,
    attendance_status: "PRESENT",
    daily_report: ""
  });

  const { data: reports } = useQuery({ queryKey: ["sales-team-reports"], queryFn: fetchSalesTeamReports });
  const { data: leaderboard } = useQuery({ queryKey: ["sales-team-leaderboard"], queryFn: fetchSalesTeamLeaderboard });

  const createMutation = useMutation({
    mutationFn: createSalesTeamReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sales-team-reports"] });
      queryClient.invalidateQueries({ queryKey: ["sales-team-leaderboard"] });
      setForm({
        report_date: "",
        sales_executive_id: "",
        sales_executive_name: "",
        target_value: 0,
        achieved_sales_value: 0,
        bookings_count: 0,
        commission_value: 0,
        site_visits_count: 0,
        attendance_status: "PRESENT",
        daily_report: ""
      });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      report_date: form.report_date,
      sales_executive_id: form.sales_executive_id,
      sales_executive_name: form.sales_executive_name,
      target_value: Number(form.target_value),
      achieved_sales_value: Number(form.achieved_sales_value),
      bookings_count: Number(form.bookings_count),
      commission_value: Number(form.commission_value),
      site_visits_count: Number(form.site_visits_count),
      attendance_status: form.attendance_status,
      daily_report: form.daily_report || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Sales Team CRM</h1>
        <p className="text-steel mt-2">Track sales executives, targets, sales, bookings, commission, site visits, attendance, daily reports, and leaderboard.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.report_date} onChange={(e) => setForm((s) => ({ ...s, report_date: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Sales Executive User ID" value={form.sales_executive_id} onChange={(e) => setForm((s) => ({ ...s, sales_executive_id: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Sales Executive Name" value={form.sales_executive_name} onChange={(e) => setForm((s) => ({ ...s, sales_executive_name: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Target" value={form.target_value} onChange={(e) => setForm((s) => ({ ...s, target_value: Number(e.target.value) }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Sales" value={form.achieved_sales_value} onChange={(e) => setForm((s) => ({ ...s, achieved_sales_value: Number(e.target.value) }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Bookings" value={form.bookings_count} onChange={(e) => setForm((s) => ({ ...s, bookings_count: Number(e.target.value) }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Commission" value={form.commission_value} onChange={(e) => setForm((s) => ({ ...s, commission_value: Number(e.target.value) }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Site Visits" value={form.site_visits_count} onChange={(e) => setForm((s) => ({ ...s, site_visits_count: Number(e.target.value) }))} />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.attendance_status} onChange={(e) => setForm((s) => ({ ...s, attendance_status: e.target.value }))}>
            {ATTENDANCE.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
          <input className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-3" placeholder="Daily Report" value={form.daily_report} onChange={(e) => setForm((s) => ({ ...s, daily_report: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Add Team Report</button>
        </form>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="card p-5">
          <h2 className="font-display text-xl text-ink">Leaderboards</h2>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(leaderboard ?? []).map((row, index) => (
              <div key={row.sales_executive_id} className="rounded-lg border border-slate-100 p-2">
                <div className="font-semibold text-ink">#{index + 1} {row.sales_executive_name}</div>
                <div>Target: {row.target_value} | Sales: {row.achieved_sales_value} | Achv: {row.achievement_percent}%</div>
                <div>Bookings: {row.bookings_count} | Commission: {row.commission_value} | Site Visits: {row.site_visits_count}</div>
              </div>
            ))}
            {(leaderboard ?? []).length === 0 ? <div>No leaderboard data yet.</div> : null}
          </div>
        </article>

        <article className="card p-5">
          <h2 className="font-display text-xl text-ink">Daily Reports</h2>
          <div className="mt-3 space-y-2 text-sm text-steel max-h-80 overflow-auto">
            {(reports ?? []).map((row) => (
              <div key={row.id} className="rounded-lg border border-slate-100 p-2">
                <div className="font-semibold text-ink">{row.sales_executive_name} ({row.report_date})</div>
                <div>Attendance: {row.attendance_status} | Bookings: {row.bookings_count} | Site Visits: {row.site_visits_count}</div>
                <div>Target: {row.target_value} | Sales: {row.achieved_sales_value} | Commission: {row.commission_value}</div>
                <div>Report: {row.daily_report ?? "-"}</div>
              </div>
            ))}
            {(reports ?? []).length === 0 ? <div>No sales team reports yet.</div> : null}
          </div>
        </article>
      </section>
    </div>
  );
}
