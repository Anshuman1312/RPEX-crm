import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createLead, fetchLeads, updateLeadStatus } from "../services/crm";

const STATUS_OPTIONS = ["NEW", "CONTACTED", "FOLLOW_UP", "INTERESTED", "SITE_VISIT", "NEGOTIATION", "BOOKING", "LOST", "FUTURE"] as const;
const SOURCE_OPTIONS = ["FACEBOOK", "INSTAGRAM", "GOOGLE_ADS", "WEBSITE", "WHATSAPP", "REFERRAL", "WALK_IN", "CALL", "MAGICBRICKS", "99ACRES", "HOUSING_COM"] as const;

const STATUS_LABELS: Record<(typeof STATUS_OPTIONS)[number], string> = {
  NEW: "New",
  CONTACTED: "Contacted",
  FOLLOW_UP: "Follow Up",
  INTERESTED: "Interested",
  SITE_VISIT: "Site Visit",
  NEGOTIATION: "Negotiation",
  BOOKING: "Booking",
  LOST: "Lost",
  FUTURE: "Future"
};

const SOURCE_LABELS: Record<(typeof SOURCE_OPTIONS)[number], string> = {
  FACEBOOK: "Facebook",
  INSTAGRAM: "Instagram",
  GOOGLE_ADS: "Google Ads",
  WEBSITE: "Website",
  WHATSAPP: "WhatsApp",
  REFERRAL: "Referral",
  WALK_IN: "Walk-in",
  CALL: "Call",
  MAGICBRICKS: "MagicBricks",
  "99ACRES": "99acres",
  HOUSING_COM: "Housing.com"
};

export default function LeadsPage() {
  const queryClient = useQueryClient();
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [source, setSource] = useState("");
  const [page, setPage] = useState(1);
  const [leadForm, setLeadForm] = useState({
    name: "",
    phone: "",
    email: "",
    source: "FACEBOOK",
    status: "NEW",
    budget: "",
    preferred_location: "",
    property_type: "",
    notes: "",
    interested_project: "",
    assigned_to: "",
    assigned_to_name: "",
    lead_score: ""
  });

  const { data, isLoading } = useQuery({
    queryKey: ["leads", q, source, status, page],
    queryFn: () =>
      fetchLeads({
        q,
        statuses: status || undefined,
        source: source || undefined,
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

  const createMutation = useMutation({
    mutationFn: createLead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      setLeadForm({
        name: "",
        phone: "",
        email: "",
        source: "FACEBOOK",
        status: "NEW",
        budget: "",
        preferred_location: "",
        property_type: "",
        notes: "",
        interested_project: "",
        assigned_to: "",
        assigned_to_name: "",
        lead_score: ""
      });
    }
  });

  function handleFilterSubmit(event: FormEvent) {
    event.preventDefault();
    setPage(1);
  }

  function handleCreateLead(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      name: leadForm.name,
      phone: leadForm.phone,
      email: leadForm.email,
      source: leadForm.source,
      status: leadForm.status,
      budget: leadForm.budget || null,
      preferred_location: leadForm.preferred_location || null,
      property_type: leadForm.property_type || null,
      notes: leadForm.notes || null,
      interested_project: leadForm.interested_project || null,
      assigned_to: leadForm.assigned_to || null,
      assigned_to_name: leadForm.assigned_to_name || null,
      lead_score: leadForm.lead_score ? Number(leadForm.lead_score) : null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Lead Management</h1>
        <p className="text-steel mt-2">Track, prioritize, and update lead lifecycle in real time.</p>

        <form className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={handleCreateLead}>
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Name" value={leadForm.name} onChange={(e) => setLeadForm((s) => ({ ...s, name: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Phone" value={leadForm.phone} onChange={(e) => setLeadForm((s) => ({ ...s, phone: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="email" placeholder="Email" value={leadForm.email} onChange={(e) => setLeadForm((s) => ({ ...s, email: e.target.value }))} required />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={leadForm.source} onChange={(e) => setLeadForm((s) => ({ ...s, source: e.target.value }))}>
            {SOURCE_OPTIONS.map((option) => <option key={option} value={option}>{SOURCE_LABELS[option]}</option>)}
          </select>

          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Budget" value={leadForm.budget} onChange={(e) => setLeadForm((s) => ({ ...s, budget: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Preferred Location" value={leadForm.preferred_location} onChange={(e) => setLeadForm((s) => ({ ...s, preferred_location: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Property Type" value={leadForm.property_type} onChange={(e) => setLeadForm((s) => ({ ...s, property_type: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Interested Project" value={leadForm.interested_project} onChange={(e) => setLeadForm((s) => ({ ...s, interested_project: e.target.value }))} />

          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Assigned To (User ID)" value={leadForm.assigned_to} onChange={(e) => setLeadForm((s) => ({ ...s, assigned_to: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Assigned To (Name)" value={leadForm.assigned_to_name} onChange={(e) => setLeadForm((s) => ({ ...s, assigned_to_name: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" min={0} max={100} placeholder="Lead Score (0-100)" value={leadForm.lead_score} onChange={(e) => setLeadForm((s) => ({ ...s, lead_score: e.target.value }))} />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={leadForm.status} onChange={(e) => setLeadForm((s) => ({ ...s, status: e.target.value }))}>
            {STATUS_OPTIONS.map((option) => <option key={option} value={option}>{STATUS_LABELS[option]}</option>)}
          </select>

          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-4" rows={2} placeholder="Notes" value={leadForm.notes} onChange={(e) => setLeadForm((s) => ({ ...s, notes: e.target.value }))} />
          <button className="btn-primary px-4 py-2 md:col-span-4">Create Lead</button>
        </form>

        <form className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={handleFilterSubmit}>
          <input
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Search by name, email, phone"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="">All Sources</option>
            {SOURCE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {SOURCE_LABELS[option]}
              </option>
            ))}
          </select>
          <select className="rounded-xl border border-slate-200 px-3 py-2" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All Status</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {STATUS_LABELS[option]}
              </option>
            ))}
          </select>
          <button className="btn-primary px-4 py-2 md:col-span-4">Apply Filters</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Contact</th>
                <th className="text-left px-4 py-3">Source</th>
                <th className="text-left px-4 py-3">Details</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Created</th>
                <th className="text-left px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td className="px-4 py-4" colSpan={7}>
                    Loading leads...
                  </td>
                </tr>
              ) : (
                (data?.items ?? []).map((lead) => (
                  <tr key={lead.id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-semibold text-ink" data-label="Name">{lead.name}</td>
                    <td className="px-4 py-3 text-steel" data-label="Contact">
                      <div>{lead.email}</div>
                      <div>{lead.phone}</div>
                    </td>
                    <td className="px-4 py-3 text-steel" data-label="Source">{lead.source ? SOURCE_LABELS[(lead.source as keyof typeof SOURCE_LABELS)] ?? lead.source : "-"}</td>
                    <td className="px-4 py-3 text-steel" data-label="Details">
                      <div>Budget: {(lead.extra_data?.budget as string) ?? "-"}</div>
                      <div>Location: {(lead.extra_data?.preferred_location as string) ?? "-"}</div>
                      <div>Type: {(lead.extra_data?.property_type as string) ?? "-"}</div>
                      <div>Project: {(lead.extra_data?.interested_project as string) ?? "-"}</div>
                      <div>Assigned: {(lead.extra_data?.assigned_to_name as string) ?? lead.assigned_to ?? "-"}</div>
                      <div>Score: {String(lead.extra_data?.lead_score ?? "-")}</div>
                    </td>
                    <td className="px-4 py-3" data-label="Status">
                      <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold">{STATUS_LABELS[(lead.status as keyof typeof STATUS_LABELS)] ?? lead.status}</span>
                    </td>
                    <td className="px-4 py-3 text-steel" data-label="Created">{new Date(lead.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3" data-label="Action">
                      <select
                        className="rounded-lg border border-slate-200 px-2 py-1"
                        value={lead.status}
                        onChange={(e) => statusMutation.mutate({ leadId: lead.id, nextStatus: e.target.value })}
                      >
                        {STATUS_OPTIONS.map((option) => (
                          <option key={option} value={option}>
                            {STATUS_LABELS[option]}
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
