import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createCampaign, fetchCampaigns } from "../services/crm";

export default function CampaignsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    type: "Google Ads",
    platform: "Google",
    budget: 0,
    start_date: "",
    end_date: ""
  });

  const { data } = useQuery({ queryKey: ["campaigns"], queryFn: fetchCampaigns });

  const createMutation = useMutation({
    mutationFn: createCampaign,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      setForm({ name: "", type: "Google Ads", platform: "Google", budget: 0, start_date: "", end_date: "" });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      name: form.name,
      type: form.type,
      platform: form.platform,
      budget: Number(form.budget),
      start_date: form.start_date || null,
      end_date: form.end_date || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Campaign Control Center</h1>
        <p className="text-steel mt-2">Configure budgeted channels and monitor active acquisition streams.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Campaign name"
            value={form.name}
            onChange={(e) => setForm((current) => ({ ...current, name: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Platform"
            value={form.platform}
            onChange={(e) => setForm((current) => ({ ...current, platform: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            placeholder="Type"
            value={form.type}
            onChange={(e) => setForm((current) => ({ ...current, type: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            placeholder="Budget"
            value={form.budget}
            onChange={(e) => setForm((current) => ({ ...current, budget: Number(e.target.value) }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="date"
            value={form.start_date}
            onChange={(e) => setForm((current) => ({ ...current, start_date: e.target.value }))}
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="date"
            value={form.end_date}
            onChange={(e) => setForm((current) => ({ ...current, end_date: e.target.value }))}
          />
          <button className="btn-primary px-4 py-2 md:col-span-3">Create Campaign</button>
        </form>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(data ?? []).map((campaign) => (
          <article key={campaign.id} className="card p-5">
            <h2 className="font-display text-xl text-ink">{campaign.name}</h2>
            <p className="text-steel mt-1">{campaign.type} | {campaign.platform}</p>
            <p className="mt-3 text-sm">Budget: <span className="font-semibold">{campaign.budget}</span></p>
            <p className="text-sm text-steel">{campaign.start_date ?? "-"} to {campaign.end_date ?? "-"}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
