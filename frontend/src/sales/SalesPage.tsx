import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createBooking, fetchBookings } from "../services/crm";

export default function SalesPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    customer_id: "",
    project_name: "",
    unit_code: "",
    booking_value: 0,
    booking_date: "",
    partner_user_id: ""
  });

  const { data, isLoading } = useQuery({ queryKey: ["bookings"], queryFn: fetchBookings });

  const createMutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      setForm({ customer_id: "", project_name: "", unit_code: "", booking_value: 0, booking_date: "", partner_user_id: "" });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      customer_id: form.customer_id,
      project_name: form.project_name,
      unit_code: form.unit_code || null,
      booking_value: Number(form.booking_value),
      booking_date: form.booking_date,
      partner_user_id: form.partner_user_id || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Sales CRM</h1>
        <p className="text-steel mt-2">Capture bookings and track sales execution.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer ID" value={form.customer_id} onChange={(e) => setForm((s) => ({ ...s, customer_id: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Project" value={form.project_name} onChange={(e) => setForm((s) => ({ ...s, project_name: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Unit Code" value={form.unit_code} onChange={(e) => setForm((s) => ({ ...s, unit_code: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Booking Value" value={form.booking_value} onChange={(e) => setForm((s) => ({ ...s, booking_value: Number(e.target.value) }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.booking_date} onChange={(e) => setForm((s) => ({ ...s, booking_date: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Partner User ID" value={form.partner_user_id} onChange={(e) => setForm((s) => ({ ...s, partner_user_id: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Create Booking</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Booking</th>
                <th className="text-left px-4 py-3">Customer</th>
                <th className="text-left px-4 py-3">Value</th>
                <th className="text-left px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={4}>Loading bookings...</td></tr>
              ) : (
                (data ?? []).map((row) => (
                  <tr key={row.id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-semibold text-ink" data-label="Booking">{row.project_name}</td>
                    <td className="px-4 py-3 text-steel" data-label="Customer">{row.customer_id}</td>
                    <td className="px-4 py-3 text-steel" data-label="Value">{row.booking_value}</td>
                    <td className="px-4 py-3 text-steel" data-label="Status">{row.status}</td>
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
