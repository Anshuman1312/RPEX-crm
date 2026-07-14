import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createKeyword, fetchCampaigns, fetchKeywords } from "../services/crm";

export default function KeywordsPage() {
  const queryClient = useQueryClient();
  const { data: campaigns } = useQuery({ queryKey: ["campaigns"], queryFn: fetchCampaigns });
  const { data: keywords } = useQuery({ queryKey: ["keywords"], queryFn: fetchKeywords });

  const initialCampaignId = useMemo(() => campaigns?.[0]?.id ?? "", [campaigns]);
  const [form, setForm] = useState({
    keyword: "",
    url: "",
    campaign_id: "",
    target_position: 10,
    current_position: 100,
    traffic: 0,
    clicks: 0,
    impressions: 0
  });

  const mutation = useMutation({
    mutationFn: createKeyword,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["keywords"] });
      setForm((current) => ({ ...current, keyword: "", url: "" }));
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    mutation.mutate({
      keyword: form.keyword,
      url: form.url,
      campaign_id: form.campaign_id || initialCampaignId,
      target_position: Number(form.target_position),
      current_position: Number(form.current_position),
      traffic: Number(form.traffic),
      clicks: Number(form.clicks),
      impressions: Number(form.impressions)
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Keyword Intelligence</h1>
        <p className="text-steel mt-2">Track ranking delta, traffic potential, and impression trends per campaign.</p>

        <form className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3" onSubmit={handleSubmit}>
          <input
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Keyword"
            value={form.keyword}
            onChange={(e) => setForm((current) => ({ ...current, keyword: e.target.value }))}
            required
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2"
            placeholder="Landing URL"
            value={form.url}
            onChange={(e) => setForm((current) => ({ ...current, url: e.target.value }))}
            required
          />
          <select
            className="rounded-xl border border-slate-200 px-3 py-2"
            value={form.campaign_id || initialCampaignId}
            onChange={(e) => setForm((current) => ({ ...current, campaign_id: e.target.value }))}
          >
            {(campaigns ?? []).map((campaign) => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            placeholder="Target position"
            value={form.target_position}
            onChange={(e) => setForm((current) => ({ ...current, target_position: Number(e.target.value) }))}
          />
          <input
            className="rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            placeholder="Current position"
            value={form.current_position}
            onChange={(e) => setForm((current) => ({ ...current, current_position: Number(e.target.value) }))}
          />
          <button className="btn-primary px-4 py-2">Add Keyword</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">Keyword</th>
                <th className="text-left px-4 py-3">URL</th>
                <th className="text-left px-4 py-3">Target</th>
                <th className="text-left px-4 py-3">Current</th>
                <th className="text-left px-4 py-3">Traffic</th>
              </tr>
            </thead>
            <tbody>
              {(keywords ?? []).map((keyword) => (
                <tr key={keyword.id} className="border-t border-slate-100">
                  <td className="px-4 py-3 font-semibold text-ink">{keyword.keyword}</td>
                  <td className="px-4 py-3 text-steel">{keyword.url}</td>
                  <td className="px-4 py-3">{keyword.target_position ?? "-"}</td>
                  <td className="px-4 py-3">{keyword.current_position ?? "-"}</td>
                  <td className="px-4 py-3">{keyword.traffic}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
