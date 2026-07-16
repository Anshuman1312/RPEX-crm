import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createBooking, fetchBookingDocuments, fetchBookings, type BookingDocuments } from "../services/crm";

const PAYMENT_METHODS = ["CASH", "UPI", "CARD", "NET_BANKING", "CHEQUE", "LOAN"] as const;

export default function SalesPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    customer_id: "",
    project_name: "",
    unit_code: "",
    booking_value: 0,
    booking_date: "",
    payment_method: "",
    receipt: "",
    plot_number: "",
    agreement_date: "",
    emi_details: "",
    loan_required: false,
    kyc_documents: "",
    partner_user_id: ""
  });
  const [documentsByBooking, setDocumentsByBooking] = useState<Record<string, BookingDocuments>>({});

  const { data, isLoading } = useQuery({ queryKey: ["bookings"], queryFn: fetchBookings });

  const createMutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      setForm({
        customer_id: "",
        project_name: "",
        unit_code: "",
        booking_value: 0,
        booking_date: "",
        payment_method: "",
        receipt: "",
        plot_number: "",
        agreement_date: "",
        emi_details: "",
        loan_required: false,
        kyc_documents: "",
        partner_user_id: ""
      });
    }
  });

  const documentsMutation = useMutation({
    mutationFn: fetchBookingDocuments,
    onSuccess: (docs, bookingId) => {
      setDocumentsByBooking((state) => ({ ...state, [bookingId]: docs }));
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
      payment_method: form.payment_method || null,
      receipt: form.receipt || null,
      plot_number: form.plot_number || null,
      agreement_date: form.agreement_date || null,
      emi_details: form.emi_details || null,
      loan_required: form.loan_required,
      kyc_documents: form.kyc_documents
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
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
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Plot Number" value={form.plot_number} onChange={(e) => setForm((s) => ({ ...s, plot_number: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Booking Value" value={form.booking_value} onChange={(e) => setForm((s) => ({ ...s, booking_value: Number(e.target.value) }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.booking_date} onChange={(e) => setForm((s) => ({ ...s, booking_date: e.target.value }))} required />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.payment_method} onChange={(e) => setForm((s) => ({ ...s, payment_method: e.target.value }))}>
            <option value="">Payment Method</option>
            {PAYMENT_METHODS.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Receipt URL / Ref" value={form.receipt} onChange={(e) => setForm((s) => ({ ...s, receipt: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.agreement_date} onChange={(e) => setForm((s) => ({ ...s, agreement_date: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="EMI Details" value={form.emi_details} onChange={(e) => setForm((s) => ({ ...s, emi_details: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" placeholder="KYC Documents (comma separated)" value={form.kyc_documents} onChange={(e) => setForm((s) => ({ ...s, kyc_documents: e.target.value }))} />
          <label className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-steel">
            <input type="checkbox" checked={form.loan_required} onChange={(e) => setForm((s) => ({ ...s, loan_required: e.target.checked }))} />
            Loan Required
          </label>
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
                <th className="text-left px-4 py-3">Plot</th>
                <th className="text-left px-4 py-3">Value</th>
                <th className="text-left px-4 py-3">Payment Method</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Generate</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={7}>Loading bookings...</td></tr>
              ) : (
                (data ?? []).map((row) => (
                  <>
                    <tr key={row.id} className="border-t border-slate-100">
                      <td className="px-4 py-3 font-semibold text-ink" data-label="Booking">{row.project_name}</td>
                      <td className="px-4 py-3 text-steel" data-label="Customer">{row.customer_id}</td>
                      <td className="px-4 py-3 text-steel" data-label="Plot">{row.plot_number ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Value">{row.booking_value}</td>
                      <td className="px-4 py-3 text-steel" data-label="Payment Method">{row.payment_method ?? "-"}</td>
                      <td className="px-4 py-3 text-steel" data-label="Status">{row.status}</td>
                      <td className="px-4 py-3" data-label="Generate">
                        <button className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50" onClick={() => documentsMutation.mutate(row.id)} type="button">
                          Generate Docs
                        </button>
                      </td>
                    </tr>
                    {documentsByBooking[row.id] ? (
                      <tr className="border-t border-slate-100 bg-slate-50/60">
                        <td className="px-4 py-3 text-xs text-slate-700" colSpan={7}>
                          <div className="font-semibold text-slate-800">Generated</div>
                          <div className="mt-1">Booking Receipt: {JSON.stringify(documentsByBooking[row.id].booking_receipt)}</div>
                          <div className="mt-1">Booking Form: {JSON.stringify(documentsByBooking[row.id].booking_form)}</div>
                          <div className="mt-1">
                            Agreement Checklist: {documentsByBooking[row.id].agreement_checklist.items.map((item) => `${item.done ? "[x]" : "[ ]"} ${item.name}`).join(" | ")}
                          </div>
                        </td>
                      </tr>
                    ) : null}
                  </>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
