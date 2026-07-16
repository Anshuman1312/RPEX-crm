import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createSiteVisit, fetchSiteVisits } from "../services/crm";

const ATTENDANCE_OPTIONS = ["PENDING", "PRESENT", "NO_SHOW", "CANCELLED"] as const;
const OUTCOME_OPTIONS = ["INTERESTED", "FOLLOW_UP", "NEGOTIATION", "BOOKING", "LOST", "FUTURE"] as const;

export default function SiteVisitsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    visit_date: "",
    visit_time: "",
    customer_name: "",
    sales_executive: "",
    pickup_required: false,
    vehicle_assigned: "",
    driver: "",
    attendance: "PENDING",
    feedback: "",
    outcome: "FOLLOW_UP"
  });

  const { data, isLoading } = useQuery({ queryKey: ["site-visits"], queryFn: fetchSiteVisits });

  const createMutation = useMutation({
    mutationFn: createSiteVisit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["site-visits"] });
      setForm({
        visit_date: "",
        visit_time: "",
        customer_name: "",
        sales_executive: "",
        pickup_required: false,
        vehicle_assigned: "",
        driver: "",
        attendance: "PENDING",
        feedback: "",
        outcome: "FOLLOW_UP"
      });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      visit_date: form.visit_date,
      visit_time: form.visit_time,
      customer_name: form.customer_name,
      sales_executive: form.sales_executive,
      pickup_required: form.pickup_required,
      vehicle_assigned: form.vehicle_assigned || null,
      driver: form.driver || null,
      attendance: form.attendance,
      feedback: form.feedback || null,
      outcome: form.outcome || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Site Visit Management</h1>
        <p className="text-steel mt-2">Plan and track visits with logistics, attendance, feedback, and outcomes.</p>

        <form className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3" onSubmit={handleSubmit}>
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.visit_date} onChange={(e) => setForm((s) => ({ ...s, visit_date: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="time" value={form.visit_time} onChange={(e) => setForm((s) => ({ ...s, visit_time: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer" value={form.customer_name} onChange={(e) => setForm((s) => ({ ...s, customer_name: e.target.value }))} required />

          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Sales Executive" value={form.sales_executive} onChange={(e) => setForm((s) => ({ ...s, sales_executive: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Vehicle Assigned" value={form.vehicle_assigned} onChange={(e) => setForm((s) => ({ ...s, vehicle_assigned: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Driver" value={form.driver} onChange={(e) => setForm((s) => ({ ...s, driver: e.target.value }))} />

          <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.attendance} onChange={(e) => setForm((s) => ({ ...s, attendance: e.target.value }))}>
            {ATTENDANCE_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
          </select>
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.outcome} onChange={(e) => setForm((s) => ({ ...s, outcome: e.target.value }))}>
            {OUTCOME_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
          </select>
          <label className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-steel">
            <input type="checkbox" checked={form.pickup_required} onChange={(e) => setForm((s) => ({ ...s, pickup_required: e.target.checked }))} />
            Pick-up Required
          </label>

          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-3" rows={2} placeholder="Feedback" value={form.feedback} onChange={(e) => setForm((s) => ({ ...s, feedback: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Add Site Visit</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Visit Date</th>
                <th className="text-left px-4 py-3">Visit Time</th>
                <th className="text-left px-4 py-3">Customer</th>
                <th className="text-left px-4 py-3">Sales Executive</th>
                <th className="text-left px-4 py-3">Pick-up Required</th>
                <th className="text-left px-4 py-3">Vehicle Assigned</th>
                <th className="text-left px-4 py-3">Driver</th>
                <th className="text-left px-4 py-3">Attendance</th>
                <th className="text-left px-4 py-3">Feedback</th>
                <th className="text-left px-4 py-3">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={10}>Loading site visits...</td></tr>
              ) : (
                (data ?? []).map((row) => (
                  <tr key={row.id} className="border-t border-slate-100">
                    <td className="px-4 py-3" data-label="Visit Date">{row.visit_date}</td>
                    <td className="px-4 py-3" data-label="Visit Time">{String(row.visit_time).slice(0, 5)}</td>
                    <td className="px-4 py-3 font-semibold text-ink" data-label="Customer">{row.customer_name}</td>
                    <td className="px-4 py-3 text-steel" data-label="Sales Executive">{row.sales_executive}</td>
                    <td className="px-4 py-3 text-steel" data-label="Pick-up Required">{row.pickup_required ? "Yes" : "No"}</td>
                    <td className="px-4 py-3 text-steel" data-label="Vehicle Assigned">{row.vehicle_assigned ?? "-"}</td>
                    <td className="px-4 py-3 text-steel" data-label="Driver">{row.driver ?? "-"}</td>
                    <td className="px-4 py-3 text-steel" data-label="Attendance">{row.attendance}</td>
                    <td className="px-4 py-3 text-steel" data-label="Feedback">{row.feedback ?? "-"}</td>
                    <td className="px-4 py-3 text-steel" data-label="Outcome">{row.outcome ?? "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
