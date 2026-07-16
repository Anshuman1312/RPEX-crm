import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createFollowup, fetchFollowups, updateFollowup } from "../services/crm";

const FOLLOWUP_STATUS_OPTIONS = ["PENDING", "SCHEDULED", "DONE", "MISSED", "CANCELLED"] as const;

export default function FollowupsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    lead_id: "",
    assigned_to: "",
    followup_date: "",
    next_followup_date: "",
    remark: "",
    call_notes: "",
    whatsapp_notes: "",
    meeting_notes: "",
    voice_recording_url: "",
    sms_log: "",
    auto_reminder_enabled: true,
    status: "PENDING"
  });

  const { data } = useQuery({ queryKey: ["followups"], queryFn: fetchFollowups });
  const mutation = useMutation({
    mutationFn: createFollowup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["followups"] });
      setForm({
        lead_id: "",
        assigned_to: "",
        followup_date: "",
        next_followup_date: "",
        remark: "",
        call_notes: "",
        whatsapp_notes: "",
        meeting_notes: "",
        voice_recording_url: "",
        sms_log: "",
        auto_reminder_enabled: true,
        status: "PENDING"
      });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateFollowup(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["followups"] })
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const smsRows = form.sms_log
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => ({ type: "manual", message: line }));

    mutation.mutate({
      lead_id: form.lead_id,
      assigned_to: form.assigned_to,
      followup_date: form.followup_date,
      next_followup_date: form.next_followup_date || null,
      remark: form.remark,
      call_notes: form.call_notes || null,
      whatsapp_notes: form.whatsapp_notes || null,
      meeting_notes: form.meeting_notes || null,
      voice_recording_url: form.voice_recording_url || null,
      sms_log: smsRows,
      auto_reminder_enabled: form.auto_reminder_enabled,
      status: form.status
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Follow-up Planner</h1>
        <p className="text-steel mt-2">Manage reminders, next follow-ups, call/WhatsApp/meeting notes, voice records, and SMS logs.</p>

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
            type="datetime-local"
            value={form.next_followup_date}
            onChange={(e) => setForm((current) => ({ ...current, next_followup_date: e.target.value }))}
            placeholder="Next Follow-up Date"
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Main Remark"
            value={form.remark}
            onChange={(e) => setForm((current) => ({ ...current, remark: e.target.value }))}
            required
          />
          <select
            className="rounded-xl border border-slate-200 px-3 py-2"
            value={form.status}
            onChange={(e) => setForm((current) => ({ ...current, status: e.target.value }))}
          >
            {FOLLOWUP_STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>

          <textarea
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Call Notes"
            value={form.call_notes}
            onChange={(e) => setForm((current) => ({ ...current, call_notes: e.target.value }))}
          />
          <textarea
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="WhatsApp Notes"
            value={form.whatsapp_notes}
            onChange={(e) => setForm((current) => ({ ...current, whatsapp_notes: e.target.value }))}
          />

          <textarea
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Meeting Notes"
            value={form.meeting_notes}
            onChange={(e) => setForm((current) => ({ ...current, meeting_notes: e.target.value }))}
          />

          <input
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Voice Recording URL"
            value={form.voice_recording_url}
            onChange={(e) => setForm((current) => ({ ...current, voice_recording_url: e.target.value }))}
          />

          <textarea
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="SMS Log (one message per line)"
            value={form.sms_log}
            onChange={(e) => setForm((current) => ({ ...current, sms_log: e.target.value }))}
          />
          <label className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-steel md:col-span-2">
            <input
              type="checkbox"
              checked={form.auto_reminder_enabled}
              onChange={(e) => setForm((current) => ({ ...current, auto_reminder_enabled: e.target.checked }))}
            />
            Auto reminders enabled
          </label>
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
                <th className="text-left px-4 py-3">Next Follow-up</th>
                <th className="text-left px-4 py-3">Notes</th>
                <th className="text-left px-4 py-3">Voice</th>
                <th className="text-left px-4 py-3">SMS Log</th>
                <th className="text-left px-4 py-3">History</th>
                <th className="text-left px-4 py-3">Remark</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Auto Reminder</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((row) => (
                <tr key={row.id} className="border-t border-slate-100">
                  <td className="px-4 py-3" data-label="Lead ID">{row.lead_id}</td>
                  <td className="px-4 py-3" data-label="Date">{new Date(row.followup_date).toLocaleString()}</td>
                  <td className="px-4 py-3" data-label="Next Follow-up">{row.next_followup_date ? new Date(row.next_followup_date).toLocaleString() : "-"}</td>
                  <td className="px-4 py-3 text-steel" data-label="Notes">
                    <div><strong>Call:</strong> {row.call_notes ?? "-"}</div>
                    <div><strong>WhatsApp:</strong> {row.whatsapp_notes ?? "-"}</div>
                    <div><strong>Meeting:</strong> {row.meeting_notes ?? "-"}</div>
                  </td>
                  <td className="px-4 py-3 text-steel" data-label="Voice">
                    {row.voice_recording_url ? <a className="text-cyan-300 underline" href={row.voice_recording_url} target="_blank" rel="noreferrer">Listen</a> : "-"}
                  </td>
                  <td className="px-4 py-3 text-steel" data-label="SMS Log">
                    {(row.sms_log ?? []).length ? (
                      <div className="space-y-1">
                        {(row.sms_log ?? []).slice(0, 3).map((log, idx) => <div key={idx}>{String(log.message ?? "-")}</div>)}
                      </div>
                    ) : "-"}
                  </td>
                  <td className="px-4 py-3 text-steel" data-label="History">
                    {(row.followup_history ?? []).length ? (
                      <div className="space-y-1">
                        {(row.followup_history ?? []).slice(-2).map((entry, idx) => (
                          <div key={idx}>{String(entry.action ?? "update")} | {String(entry.at ?? "-")}</div>
                        ))}
                      </div>
                    ) : "-"}
                  </td>
                  <td className="px-4 py-3 text-steel" data-label="Remark">{row.remark}</td>
                  <td className="px-4 py-3" data-label="Status">
                    <select
                      className="rounded-lg border border-slate-200 px-2 py-1"
                      value={row.status}
                      onChange={(e) => updateMutation.mutate({ id: row.id, status: e.target.value })}
                    >
                      {FOLLOWUP_STATUS_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3" data-label="Auto Reminder">{row.auto_reminder_enabled ? "Enabled" : "Disabled"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
