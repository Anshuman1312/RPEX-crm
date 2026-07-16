import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createTelecallingCall, fetchTelecallingCalls, fetchTelecallingPerformance } from "../services/crm";

const CALL_STATUS = ["CONNECTED", "NOT_CONNECTED", "INTERESTED"] as const;

export default function TelecallingPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    call_date: "",
    telecaller_id: "",
    lead_id: "",
    customer_name: "",
    status: "NOT_CONNECTED",
    call_duration_sec: 0,
    call_recording_url: "",
    daily_target: 0,
    notes: ""
  });

  const { data: calls } = useQuery({ queryKey: ["telecalling-calls"], queryFn: fetchTelecallingCalls });
  const { data: performance } = useQuery({ queryKey: ["telecalling-performance"], queryFn: fetchTelecallingPerformance });

  const createMutation = useMutation({
    mutationFn: createTelecallingCall,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["telecalling-calls"] });
      queryClient.invalidateQueries({ queryKey: ["telecalling-performance"] });
      setForm({
        call_date: "",
        telecaller_id: "",
        lead_id: "",
        customer_name: "",
        status: "NOT_CONNECTED",
        call_duration_sec: 0,
        call_recording_url: "",
        daily_target: 0,
        notes: ""
      });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      call_date: form.call_date,
      telecaller_id: form.telecaller_id,
      lead_id: form.lead_id || null,
      customer_name: form.customer_name,
      status: form.status,
      call_duration_sec: Number(form.call_duration_sec),
      call_recording_url: form.call_recording_url || null,
      daily_target: Number(form.daily_target),
      notes: form.notes || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Telecalling CRM</h1>
        <p className="text-steel mt-2">Capture daily calls, connected outcomes, recordings, duration, targets, and team performance.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.call_date} onChange={(e) => setForm((s) => ({ ...s, call_date: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Telecaller User ID" value={form.telecaller_id} onChange={(e) => setForm((s) => ({ ...s, telecaller_id: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Lead ID (optional)" value={form.lead_id} onChange={(e) => setForm((s) => ({ ...s, lead_id: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer" value={form.customer_name} onChange={(e) => setForm((s) => ({ ...s, customer_name: e.target.value }))} required />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.status} onChange={(e) => setForm((s) => ({ ...s, status: e.target.value }))}>
            {CALL_STATUS.map((status) => <option key={status} value={status}>{status}</option>)}
          </select>
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Call Duration (sec)" value={form.call_duration_sec} onChange={(e) => setForm((s) => ({ ...s, call_duration_sec: Number(e.target.value) }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Call Recording URL" value={form.call_recording_url} onChange={(e) => setForm((s) => ({ ...s, call_recording_url: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Daily Target" value={form.daily_target} onChange={(e) => setForm((s) => ({ ...s, daily_target: Number(e.target.value) }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Notes" value={form.notes} onChange={(e) => setForm((s) => ({ ...s, notes: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-3">Add Call Log</button>
        </form>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="card p-5">
          <h2 className="font-display text-xl text-ink">Daily Targets & Performance</h2>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(performance ?? []).map((row) => (
              <div key={row.telecaller_id} className="rounded-lg border border-slate-100 p-2">
                <div className="font-semibold text-ink">{row.telecaller_name}</div>
                <div>Calls: {row.daily_calls} / Target: {row.daily_target}</div>
                <div>Connected: {row.connected} | Not Connected: {row.not_connected} | Interested: {row.interested}</div>
                <div>Duration: {row.total_duration_sec}s | Performance: {row.performance_percent}%</div>
              </div>
            ))}
            {(performance ?? []).length === 0 ? <div>No telecalling performance yet.</div> : null}
          </div>
        </article>

        <article className="card p-5">
          <h2 className="font-display text-xl text-ink">Daily Calls</h2>
          <div className="mt-3 space-y-2 text-sm text-steel max-h-80 overflow-auto">
            {(calls ?? []).map((row) => (
              <div key={row.id} className="rounded-lg border border-slate-100 p-2">
                <div className="font-semibold text-ink">{row.customer_name} ({row.status})</div>
                <div>{row.call_date} | Duration: {row.call_duration_sec}s | Target: {row.daily_target}</div>
                <div>Recording: {row.call_recording_url ?? "-"}</div>
              </div>
            ))}
            {(calls ?? []).length === 0 ? <div>No calls logged yet.</div> : null}
          </div>
        </article>
      </section>
    </div>
  );
}
