import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createCampaign, fetchCampaigns } from "../services/crm";

const CHANNELS = ["META_ADS", "GOOGLE_ADS", "YOUTUBE", "SMS", "EMAIL", "WHATSAPP", "INFLUENCERS"] as const;

export default function CampaignsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    type: "Performance",
    platform: "Meta",
    channel: "META_ADS",
    budget: 0,
    reach: 0,
    leads: 0,
    roas: 0,
    conversion: 0,
    start_date: "",
    end_date: ""
  });

  const { data } = useQuery({ queryKey: ["campaigns"], queryFn: fetchCampaigns });

  const createMutation = useMutation({
    mutationFn: createCampaign,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      setForm({
        name: "",
        type: "Performance",
        platform: "Meta",
        channel: "META_ADS",
        budget: 0,
        reach: 0,
        leads: 0,
        roas: 0,
        conversion: 0,
        start_date: "",
        end_date: ""
      });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createMutation.mutate({
      name: form.name,
      type: form.type,
      platform: form.platform,
      channel: form.channel,
      budget: Number(form.budget),
      reach: Number(form.reach),
      leads: Number(form.leads),
      roas: Number(form.roas),
      conversion: Number(form.conversion),
      start_date: form.start_date || null,
      end_date: form.end_date || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Campaign Control Center</h1>
        <p className="text-steel mt-2">Meta Ads, Google Ads, YouTube, SMS, Email, WhatsApp, Influencers with live campaign KPI tracking.</p>

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
          <select
            className="rounded-xl border border-slate-200 px-3 py-2"
            value={form.channel}
            onChange={(e) => setForm((current) => ({ ...current, channel: e.target.value }))}
          >
            {CHANNELS.map((channel) => <option key={channel} value={channel}>{channel}</option>)}
          </select>
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
            type="number"
            placeholder="Reach"
            value={form.reach}
            onChange={(e) => setForm((current) => ({ ...current, reach: Number(e.target.value) }))}
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            placeholder="Leads"
            value={form.leads}
            onChange={(e) => setForm((current) => ({ ...current, leads: Number(e.target.value) }))}
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            step="0.01"
            placeholder="ROAS"
            value={form.roas}
            onChange={(e) => setForm((current) => ({ ...current, roas: Number(e.target.value) }))}
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            step="0.01"
            placeholder="Conversion %"
            value={form.conversion}
            onChange={(e) => setForm((current) => ({ ...current, conversion: Number(e.target.value) }))}
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

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {(data ?? []).map((campaign) => (
          <article key={campaign.id} className="card p-5">
            <h2 className="font-display text-xl text-ink">{campaign.name}</h2>
            <p className="text-steel mt-1">{campaign.type} | {campaign.platform} | {campaign.channel}</p>
            <p className="mt-3 text-sm">Budget: <span className="font-semibold">{campaign.budget}</span></p>
            <p className="text-sm text-steel">{campaign.start_date ?? "-"} to {campaign.end_date ?? "-"}</p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
              <div className="rounded-lg border border-slate-100 px-2 py-1">Reach: {campaign.reach}</div>
              <div className="rounded-lg border border-slate-100 px-2 py-1">Leads: {campaign.leads}</div>
              <div className="rounded-lg border border-slate-100 px-2 py-1">CPL: {campaign.cpl}</div>
              <div className="rounded-lg border border-slate-100 px-2 py-1">ROAS: {campaign.roas}</div>
              <div className="rounded-lg border border-slate-100 px-2 py-1 col-span-2">Conversion: {campaign.conversion}%</div>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
