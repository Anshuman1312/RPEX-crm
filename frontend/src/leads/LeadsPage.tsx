import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchLeads, updateLeadStatus } from "../services/crm";

const STATUS_OPTIONS = ["NEW", "CONTACTED", "FOLLOW_UP", "DEMO", "CONVERTED", "LOST"];

export default function LeadsPage() {
  const queryClient = useQueryClient();
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["leads", q, status, page],
    queryFn: () =>
      fetchLeads({
        q,
        statuses: status || undefined,
        page,
        page_size: 10,
        sort_by: "created_at",
        sort_order: "desc"
      })
  });

  const statusMutation = useMutation({
    mutationFn: ({ leadId, nextStatus }: { leadId: string; nextStatus: string }) => updateLeadStatus(leadId, nextStatus),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["leads"] })
  });

  function handleFilterSubmit(event: FormEvent) {
    event.preventDefault();
    setPage(1);
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Lead Management</h1>
        <p className="text-steel mt-2">Track, prioritize, and update lead lifecycle in real time.</p>

        <form className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={handleFilterSubmit}>
          <input
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Search by name, email, phone"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All Status</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <button className="btn-primary px-4 py-2">Apply Filters</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Contact</th>
                <th className="text-left px-4 py-3">Source</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Created</th>
                <th className="text-left px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td className="px-4 py-4" colSpan={6}>
                    Loading leads...
                  </td>
                </tr>
              ) : (
                (data?.items ?? []).map((lead) => (
                  <tr key={lead.id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-semibold text-ink">{lead.name}</td>
                    <td className="px-4 py-3 text-steel">
                      <div>{lead.email}</div>
                      <div>{lead.phone}</div>
                    </td>
                    <td className="px-4 py-3 text-steel">{lead.source ?? "-"}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold">{lead.status}</span>
                    </td>
                    <td className="px-4 py-3 text-steel">{new Date(lead.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3">
                      <select
                        className="rounded-lg border border-slate-200 px-2 py-1"
                        value={lead.status}
                        onChange={(e) => statusMutation.mutate({ leadId: lead.id, nextStatus: e.target.value })}
                      >
                        {STATUS_OPTIONS.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between p-4 border-t border-slate-100">
          <p className="text-sm text-steel">Total: {data?.total ?? 0}</p>
          <div className="flex items-center gap-2">
            <button
              className="rounded-lg border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
              disabled={page <= 1}
              onClick={() => setPage((current) => Math.max(current - 1, 1))}
            >
              Prev
            </button>
            <span className="text-sm text-steel">Page {page}</span>
            <button
              className="rounded-lg border border-slate-300 px-3 py-1 text-sm disabled:opacity-50"
              disabled={(data?.items?.length ?? 0) < 10}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
