import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createCustomer, fetchCustomers } from "../services/crm";

export default function CustomersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    city: "",
    partner_user_id: ""
  });

  const { data, isLoading } = useQuery({ queryKey: ["customers"], queryFn: fetchCustomers });

  const createMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      setForm({ full_name: "", email: "", phone: "", city: "", partner_user_id: "" });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      full_name: form.full_name,
      email: form.email || null,
      phone: form.phone,
      city: form.city || null,
      partner_user_id: form.partner_user_id || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Customer CRM</h1>
        <p className="text-steel mt-2">Manage customer profiles and partner mappings.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Full name" value={form.full_name} onChange={(e) => setForm((s) => ({ ...s, full_name: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm((s) => ({ ...s, email: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Phone" value={form.phone} onChange={(e) => setForm((s) => ({ ...s, phone: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="City" value={form.city} onChange={(e) => setForm((s) => ({ ...s, city: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" placeholder="Partner User ID (optional)" value={form.partner_user_id} onChange={(e) => setForm((s) => ({ ...s, partner_user_id: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Create Customer</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Contact</th>
                <th className="text-left px-4 py-3">City</th>
                <th className="text-left px-4 py-3">Partner</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={4}>Loading customers...</td></tr>
              ) : (
                (data ?? []).map((row) => (
                  <tr key={row.id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-semibold text-ink" data-label="Name">{row.full_name}</td>
                    <td className="px-4 py-3 text-steel" data-label="Contact">{row.email ?? "-"}<br />{row.phone}</td>
                    <td className="px-4 py-3 text-steel" data-label="City">{row.city ?? "-"}</td>
                    <td className="px-4 py-3 text-steel" data-label="Partner">{row.partner_user_id ?? "-"}</td>
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
