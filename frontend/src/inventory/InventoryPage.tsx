import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createInventoryUnit, fetchInventoryUnits, fetchProjects } from "../services/crm";

const STATUS_META = {
  AVAILABLE: { emoji: "🟢", label: "Available", badge: "bg-emerald-100 text-emerald-800" },
  HOLD: { emoji: "🟡", label: "Hold", badge: "bg-amber-100 text-amber-800" },
  BOOKED: { emoji: "🔵", label: "Booked", badge: "bg-sky-100 text-sky-800" },
  SOLD: { emoji: "🔴", label: "Sold", badge: "bg-rose-100 text-rose-800" }
} as const;

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    project_id: "",
    plot_no: "",
    size: "",
    facing: "",
    is_corner: false,
    price: 0,
    booking_status: "AVAILABLE" as "AVAILABLE" | "HOLD" | "BOOKED" | "SOLD",
    customer_name: "",
    sales_executive: "",
    booking_date: "",
    agreement_status: "PENDING",
    payment_status: "PENDING"
  });

  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: fetchProjects });
  const { data: units, isLoading } = useQuery({
    queryKey: ["inventory", form.project_id || "all"],
    queryFn: () => fetchInventoryUnits(form.project_id || undefined)
  });

  const createMutation = useMutation({
    mutationFn: createInventoryUnit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      setForm((current) => ({
        ...current,
        plot_no: "",
        size: "",
        facing: "",
        is_corner: false,
        price: 0,
        booking_status: "AVAILABLE",
        customer_name: "",
        sales_executive: "",
        booking_date: "",
        agreement_status: "PENDING",
        payment_status: "PENDING"
      }));
    }
  });

  const selectedProjectName = useMemo(
    () => projects?.find((project) => project.id === form.project_id)?.name ?? "Select Project",
    [projects, form.project_id]
  );

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      project_id: form.project_id,
      plot_no: form.plot_no,
      size: form.size,
      facing: form.facing || null,
      is_corner: form.is_corner,
      price: Number(form.price),
      booking_status: form.booking_status,
      customer_name: form.customer_name || null,
      sales_executive: form.sales_executive || null,
      booking_date: form.booking_date || null,
      agreement_status: form.agreement_status || null,
      payment_status: form.payment_status || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Inventory Management</h1>
        <p className="text-steel mt-2">Track plot and flat availability with booking, agreement, and payment status.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3">
          <select className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" value={form.project_id} onChange={(e) => setForm((s) => ({ ...s, project_id: e.target.value }))} required>
            <option value="">Select Project</option>
            {(projects ?? []).map((project) => (
              <option key={project.id} value={project.id}>{project.name}</option>
            ))}
          </select>
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Plot No" value={form.plot_no} onChange={(e) => setForm((s) => ({ ...s, plot_no: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Size (e.g. 1200 sqft)" value={form.size} onChange={(e) => setForm((s) => ({ ...s, size: e.target.value }))} required />

          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Facing" value={form.facing} onChange={(e) => setForm((s) => ({ ...s, facing: e.target.value }))} />
          <label className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-steel">
            <input type="checkbox" checked={form.is_corner} onChange={(e) => setForm((s) => ({ ...s, is_corner: e.target.checked }))} />
            Corner Unit
          </label>
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" min={0} placeholder="Price" value={form.price} onChange={(e) => setForm((s) => ({ ...s, price: Number(e.target.value) }))} required />

          <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.booking_status} onChange={(e) => setForm((s) => ({ ...s, booking_status: e.target.value as "AVAILABLE" | "HOLD" | "BOOKED" | "SOLD" }))}>
            <option value="AVAILABLE">🟢 Available</option>
            <option value="HOLD">🟡 Hold</option>
            <option value="BOOKED">🔵 Booked</option>
            <option value="SOLD">🔴 Sold</option>
          </select>

          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer Name" value={form.customer_name} onChange={(e) => setForm((s) => ({ ...s, customer_name: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Sales Executive" value={form.sales_executive} onChange={(e) => setForm((s) => ({ ...s, sales_executive: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.booking_date} onChange={(e) => setForm((s) => ({ ...s, booking_date: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Agreement Status" value={form.agreement_status} onChange={(e) => setForm((s) => ({ ...s, agreement_status: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Payment Status" value={form.payment_status} onChange={(e) => setForm((s) => ({ ...s, payment_status: e.target.value }))} />

          <button className="btn-primary px-4 py-2 md:col-span-4">Add Inventory Unit to {selectedProjectName}</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Plot No</th>
                <th className="text-left px-4 py-3">Size</th>
                <th className="text-left px-4 py-3">Facing</th>
                <th className="text-left px-4 py-3">Corner/Normal</th>
                <th className="text-left px-4 py-3">Price</th>
                <th className="text-left px-4 py-3">Booking Status</th>
                <th className="text-left px-4 py-3">Customer</th>
                <th className="text-left px-4 py-3">Sales Executive</th>
                <th className="text-left px-4 py-3">Booking Date</th>
                <th className="text-left px-4 py-3">Agreement</th>
                <th className="text-left px-4 py-3">Payment</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={11}>Loading inventory...</td></tr>
              ) : (
                (units ?? []).map((unit) => {
                  const meta = STATUS_META[unit.booking_status];
                  return (
                    <tr key={unit.id} className="border-t border-slate-100">
                      <td className="px-4 py-3 font-semibold text-ink" data-label="Plot No">{unit.plot_no}</td>
                      <td className="px-4 py-3 text-steel" data-label="Size">{unit.size}</td>
                      <td className="px-4 py-3 text-steel" data-label="Facing">{unit.facing ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Corner/Normal">{unit.corner_or_normal}</td>
                      <td className="px-4 py-3 text-steel" data-label="Price">{unit.price}</td>
                      <td className="px-4 py-3" data-label="Booking Status">
                        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${meta.badge}`}>
                          <span>{meta.emoji}</span>
                          <span>{meta.label}</span>
                        </span>
                      </td>
                      <td className="px-4 py-3 text-steel" data-label="Customer">{unit.customer_name ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Sales Executive">{unit.sales_executive ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Booking Date">{unit.booking_date ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Agreement">{unit.agreement_status ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Payment">{unit.payment_status ?? "-"}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
