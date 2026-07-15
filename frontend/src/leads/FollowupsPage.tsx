import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createFollowup, fetchFollowups } from "../services/crm";

export default function FollowupsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    lead_id: "",
    assigned_to: "",
    followup_date: "",
    remark: "",
    status: "PENDING"
  });

  const { data } = useQuery({ queryKey: ["followups"], queryFn: fetchFollowups });
  const mutation = useMutation({
    mutationFn: createFollowup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["followups"] });
      setForm({ lead_id: "", assigned_to: "", followup_date: "", remark: "", status: "PENDING" });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    mutation.mutate(form);
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Follow-up Planner</h1>
        <p className="text-steel mt-2">Capture callbacks and appointment notes per lead.</p>

        <form className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-3" onSubmit={handleSubmit}>
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Lead ID"
            value={form.lead_id}
            onChange={(e) => setForm((current) => ({ ...current, lead_id: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Assigned User ID"
            value={form.assigned_to}
            onChange={(e) => setForm((current) => ({ ...current, assigned_to: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="datetime-local"
            value={form.followup_date}
            onChange={(e) => setForm((current) => ({ ...current, followup_date: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Status"
            value={form.status}
            onChange={(e) => setForm((current) => ({ ...current, status: e.target.value }))}
          />
          <textarea
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Remark"
            value={form.remark}
            onChange={(e) => setForm((current) => ({ ...current, remark: e.target.value }))}
            required
          />
          <button className="btn-primary px-4 py-2 md:col-span-2">Create Follow-up</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Lead ID</th>
                <th className="text-left px-4 py-3">Date</th>
                <th className="text-left px-4 py-3">Remark</th>
                <th className="text-left px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((row) => (
                <tr key={row.id} className="border-t border-slate-100">
                  <td className="px-4 py-3" data-label="Lead ID">{row.lead_id}</td>
                  <td className="px-4 py-3" data-label="Date">{new Date(row.followup_date).toLocaleString()}</td>
                  <td className="px-4 py-3 text-steel" data-label="Remark">{row.remark}</td>
                  <td className="px-4 py-3" data-label="Status">{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
