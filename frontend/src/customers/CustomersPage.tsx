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
    birth_date: "",
    anniversary_date: "",
    family_details: "",
    documents: "",
    purchase_history: "",
    payments: "",
    site_visits: "",
    referrals: "",
    support_tickets: "",
    partner_user_id: ""
  });

  const { data, isLoading } = useQuery({ queryKey: ["customers"], queryFn: fetchCustomers });

  const createMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      setForm({
        full_name: "",
        email: "",
        phone: "",
        city: "",
        birth_date: "",
        anniversary_date: "",
        family_details: "",
        documents: "",
        purchase_history: "",
        payments: "",
        site_visits: "",
        referrals: "",
        support_tickets: "",
        partner_user_id: ""
      });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      full_name: form.full_name,
      email: form.email || null,
      phone: form.phone,
      city: form.city || null,
      birth_date: form.birth_date || null,
      anniversary_date: form.anniversary_date || null,
      extra_data: {
        personal_details: {
          email: form.email || null,
          phone: form.phone,
          city: form.city || null
        },
        family_details: form.family_details || null,
        documents: form.documents ? form.documents.split(",").map((s) => s.trim()).filter(Boolean) : [],
        purchase_history: form.purchase_history || null,
        payments: form.payments || null,
        site_visits: form.site_visits || null,
        referrals: form.referrals || null,
        support_tickets: form.support_tickets || null,
        anniversary_birthday: {
          birth_date: form.birth_date || null,
          anniversary_date: form.anniversary_date || null
        }
      },
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
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.birth_date} onChange={(e) => setForm((s) => ({ ...s, birth_date: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.anniversary_date} onChange={(e) => setForm((s) => ({ ...s, anniversary_date: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Family Details" value={form.family_details} onChange={(e) => setForm((s) => ({ ...s, family_details: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Documents (comma separated)" value={form.documents} onChange={(e) => setForm((s) => ({ ...s, documents: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Purchase History" value={form.purchase_history} onChange={(e) => setForm((s) => ({ ...s, purchase_history: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Payments" value={form.payments} onChange={(e) => setForm((s) => ({ ...s, payments: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Site Visits" value={form.site_visits} onChange={(e) => setForm((s) => ({ ...s, site_visits: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Referrals" value={form.referrals} onChange={(e) => setForm((s) => ({ ...s, referrals: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Support Tickets" value={form.support_tickets} onChange={(e) => setForm((s) => ({ ...s, support_tickets: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-3" placeholder="Partner User ID (optional)" value={form.partner_user_id} onChange={(e) => setForm((s) => ({ ...s, partner_user_id: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Create Customer</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Personal</th>
                <th className="text-left px-4 py-3">Family/Documents</th>
                <th className="text-left px-4 py-3">History/Support</th>
                <th className="text-left px-4 py-3">Partner</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={5}>Loading customers...</td></tr>
              ) : (
                (data ?? []).map((row) => (
                  <tr key={row.id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-semibold text-ink" data-label="Name">{row.full_name}</td>
                    <td className="px-4 py-3 text-steel" data-label="Personal">
                      {row.email ?? "-"}<br />{row.phone}<br />{row.city ?? "-"}
                      <br />BD: {row.birth_date ?? "-"} | ANN: {row.anniversary_date ?? "-"}
                    </td>
                    <td className="px-4 py-3 text-steel" data-label="Family/Documents">
                      Family: {String((row.extra_data?.family_details as string | null) ?? "-")}
                      <br />Docs: {Array.isArray(row.extra_data?.documents) ? (row.extra_data?.documents as string[]).join(", ") : "-"}
                    </td>
                    <td className="px-4 py-3 text-steel" data-label="History/Support">
                      Purchase: {String((row.extra_data?.purchase_history as string | null) ?? "-")}
                      <br />Payments: {String((row.extra_data?.payments as string | null) ?? "-")}
                      <br />Visits: {String((row.extra_data?.site_visits as string | null) ?? "-")}
                      <br />Referrals: {String((row.extra_data?.referrals as string | null) ?? "-")}
                      <br />Tickets: {String((row.extra_data?.support_tickets as string | null) ?? "-")}
                    </td>
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
