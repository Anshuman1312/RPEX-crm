import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createApprovalRequest,
  createInvoice,
  createPayment,
  decideApprovalRequest,
  fetchApprovalRequests,
  fetchInvoices,
  fetchPayments
} from "../services/crm";

export default function FinancePage() {
  const queryClient = useQueryClient();
  const [paymentForm, setPaymentForm] = useState({
    customer_id: "",
    booking_id: "",
    amount: 0,
    payment_date: "",
    payment_mode: "UPI",
    reference_no: ""
  });
  const [invoiceForm, setInvoiceForm] = useState({
    customer_id: "",
    booking_id: "",
    invoice_number: "",
    invoice_date: "",
    amount: 0,
    gst_amount: 0
  });

  const { data: payments } = useQuery({ queryKey: ["payments"], queryFn: fetchPayments });
  const { data: invoices } = useQuery({ queryKey: ["invoices"], queryFn: fetchInvoices });
  const { data: approvals } = useQuery({ queryKey: ["approvals"], queryFn: fetchApprovalRequests });
  const [approvalForm, setApprovalForm] = useState({
    module: "finance",
    entity_type: "invoice",
    entity_id: "",
    action: "payment_release",
    reason: ""
  });

  const paymentMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payments"] })
  });

  const invoiceMutation = useMutation({
    mutationFn: createInvoice,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["invoices"] })
  });

  const approvalCreateMutation = useMutation({
    mutationFn: createApprovalRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals"] });
      setApprovalForm({ module: "finance", entity_type: "invoice", entity_id: "", action: "payment_release", reason: "" });
    }
  });

  const approvalDecisionMutation = useMutation({
    mutationFn: ({ requestId, status }: { requestId: string; status: "APPROVED" | "REJECTED" }) =>
      decideApprovalRequest(requestId, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["approvals"] })
  });

  function submitPayment(event: FormEvent) {
    event.preventDefault();
    paymentMutation.mutate({
      customer_id: paymentForm.customer_id,
      booking_id: paymentForm.booking_id || null,
      amount: Number(paymentForm.amount),
      payment_date: paymentForm.payment_date,
      payment_mode: paymentForm.payment_mode,
      reference_no: paymentForm.reference_no || null
    });
  }

  function submitInvoice(event: FormEvent) {
    event.preventDefault();
    invoiceMutation.mutate({
      customer_id: invoiceForm.customer_id,
      booking_id: invoiceForm.booking_id || null,
      invoice_number: invoiceForm.invoice_number,
      invoice_date: invoiceForm.invoice_date,
      amount: Number(invoiceForm.amount),
      gst_amount: Number(invoiceForm.gst_amount)
    });
  }

  function submitApproval(event: FormEvent) {
    event.preventDefault();
    approvalCreateMutation.mutate({
      module: approvalForm.module,
      entity_type: approvalForm.entity_type,
      entity_id: approvalForm.entity_id,
      action: approvalForm.action,
      reason: approvalForm.reason || null,
      payload: {}
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Finance</h1>
        <p className="text-steel mt-2">Record collections and generate invoices.</p>
      </section>

      <section className="card p-6">
        <h2 className="font-display text-xl text-ink">Customer Payment</h2>
        <form onSubmit={submitPayment} className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer ID" value={paymentForm.customer_id} onChange={(e) => setPaymentForm((s) => ({ ...s, customer_id: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Booking ID" value={paymentForm.booking_id} onChange={(e) => setPaymentForm((s) => ({ ...s, booking_id: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Amount" value={paymentForm.amount} onChange={(e) => setPaymentForm((s) => ({ ...s, amount: Number(e.target.value) }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={paymentForm.payment_date} onChange={(e) => setPaymentForm((s) => ({ ...s, payment_date: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Payment mode" value={paymentForm.payment_mode} onChange={(e) => setPaymentForm((s) => ({ ...s, payment_mode: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Reference" value={paymentForm.reference_no} onChange={(e) => setPaymentForm((s) => ({ ...s, reference_no: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Add Payment</button>
        </form>
      </section>

      <section className="card p-6">
        <h2 className="font-display text-xl text-ink">Invoice</h2>
        <form onSubmit={submitInvoice} className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer ID" value={invoiceForm.customer_id} onChange={(e) => setInvoiceForm((s) => ({ ...s, customer_id: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Booking ID" value={invoiceForm.booking_id} onChange={(e) => setInvoiceForm((s) => ({ ...s, booking_id: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Invoice No" value={invoiceForm.invoice_number} onChange={(e) => setInvoiceForm((s) => ({ ...s, invoice_number: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={invoiceForm.invoice_date} onChange={(e) => setInvoiceForm((s) => ({ ...s, invoice_date: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Amount" value={invoiceForm.amount} onChange={(e) => setInvoiceForm((s) => ({ ...s, amount: Number(e.target.value) }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="GST" value={invoiceForm.gst_amount} onChange={(e) => setInvoiceForm((s) => ({ ...s, gst_amount: Number(e.target.value) }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Create Invoice</button>
        </form>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="card p-5">
          <h3 className="font-display text-lg text-ink">Recent Payments</h3>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(payments ?? []).slice(0, 5).map((row) => (
              <div key={row.id} className="rounded-lg border border-slate-100 p-2">
                {row.customer_id} | {row.amount} | {row.status}
              </div>
            ))}
          </div>
        </article>

        <article className="card p-5">
          <h3 className="font-display text-lg text-ink">Recent Invoices</h3>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(invoices ?? []).slice(0, 5).map((row) => (
              <div key={row.id} className="rounded-lg border border-slate-100 p-2">
                {row.invoice_number} | {row.amount} | {row.status}
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="card p-6">
        <h2 className="font-display text-xl text-ink">Approval Workflow</h2>
        <p className="text-steel mt-1 text-sm">Create requests for payout, invoice, or finance approval and decide pending items.</p>
        <form onSubmit={submitApproval} className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Module" value={approvalForm.module} onChange={(e) => setApprovalForm((s) => ({ ...s, module: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Entity Type" value={approvalForm.entity_type} onChange={(e) => setApprovalForm((s) => ({ ...s, entity_type: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Entity ID" value={approvalForm.entity_id} onChange={(e) => setApprovalForm((s) => ({ ...s, entity_id: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Action" value={approvalForm.action} onChange={(e) => setApprovalForm((s) => ({ ...s, action: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-3" placeholder="Reason" value={approvalForm.reason} onChange={(e) => setApprovalForm((s) => ({ ...s, reason: e.target.value }))} />
          <button className="btn-primary px-4 py-2">Create Request</button>
        </form>

        <div className="mt-5 space-y-2">
          {(approvals ?? []).slice(0, 10).map((row) => (
            <div key={row.id} className="rounded-lg border border-slate-100 p-3 text-sm">
              <div className="font-semibold text-ink">{row.module} | {row.entity_type} | {row.action}</div>
              <div className="text-steel">Entity: {row.entity_id} | Status: {row.status}</div>
              <div className="mt-2 flex gap-2">
                <button className="btn-secondary px-3 py-1 text-xs" onClick={() => approvalDecisionMutation.mutate({ requestId: row.id, status: "APPROVED" })}>
                  Approve
                </button>
                <button className="btn-secondary px-3 py-1 text-xs" onClick={() => approvalDecisionMutation.mutate({ requestId: row.id, status: "REJECTED" })}>
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
