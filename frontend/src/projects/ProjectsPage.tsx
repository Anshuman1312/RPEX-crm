import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createProject, fetchProjects } from "../services/crm";

function parseList(input: string) {
  return input
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    developer_name: "",
    sole_selling_partner: "",
    location: "",
    google_maps_url: "",
    project_status: "PLANNING",
    total_inventory: 0,
    sold_inventory: 0,
    price_list_text: "",
    payment_plans_text: "",
    documents_text: "",
    gallery_text: "",
    videos_text: "",
    brochure_url: "",
    legal_status: "",
    amenities_text: "",
    nearby_landmarks_text: ""
  });

  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: fetchProjects });

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setForm({
        name: "",
        developer_name: "",
        sole_selling_partner: "",
        location: "",
        google_maps_url: "",
        project_status: "PLANNING",
        total_inventory: 0,
        sold_inventory: 0,
        price_list_text: "",
        payment_plans_text: "",
        documents_text: "",
        gallery_text: "",
        videos_text: "",
        brochure_url: "",
        legal_status: "",
        amenities_text: "",
        nearby_landmarks_text: ""
      });
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();

    createMutation.mutate({
      name: form.name,
      developer_name: form.developer_name,
      sole_selling_partner: form.sole_selling_partner || null,
      location: form.location,
      google_maps_url: form.google_maps_url || null,
      project_status: form.project_status,
      total_inventory: Number(form.total_inventory),
      sold_inventory: Number(form.sold_inventory),
      price_list: parseList(form.price_list_text).map((line) => ({ item: line })),
      payment_plans: parseList(form.payment_plans_text).map((line) => ({ item: line })),
      documents: parseList(form.documents_text).map((line) => ({ item: line })),
      gallery: parseList(form.gallery_text).map((line) => ({ item: line })),
      videos: parseList(form.videos_text).map((line) => ({ item: line })),
      brochure: form.brochure_url ? { url: form.brochure_url } : {},
      legal_status: form.legal_status || null,
      amenities: parseList(form.amenities_text),
      nearby_landmarks: parseList(form.nearby_landmarks_text)
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Projects Registry</h1>
        <p className="text-steel mt-2">Maintain complete project information for sales and marketing operations.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Project Name" value={form.name} onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Developer Name" value={form.developer_name} onChange={(e) => setForm((s) => ({ ...s, developer_name: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" placeholder="Sole Selling / Marketing Partner" value={form.sole_selling_partner} onChange={(e) => setForm((s) => ({ ...s, sole_selling_partner: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Location" value={form.location} onChange={(e) => setForm((s) => ({ ...s, location: e.target.value }))} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Google Maps URL" value={form.google_maps_url} onChange={(e) => setForm((s) => ({ ...s, google_maps_url: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Project Status" value={form.project_status} onChange={(e) => setForm((s) => ({ ...s, project_status: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Total Inventory" value={form.total_inventory} onChange={(e) => setForm((s) => ({ ...s, total_inventory: Number(e.target.value) }))} min={0} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" placeholder="Sold Inventory" value={form.sold_inventory} onChange={(e) => setForm((s) => ({ ...s, sold_inventory: Number(e.target.value) }))} min={0} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Brochure URL" value={form.brochure_url} onChange={(e) => setForm((s) => ({ ...s, brochure_url: e.target.value }))} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Legal Status" value={form.legal_status} onChange={(e) => setForm((s) => ({ ...s, legal_status: e.target.value }))} />

          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Price List (one line per item)" value={form.price_list_text} onChange={(e) => setForm((s) => ({ ...s, price_list_text: e.target.value }))} />
          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Payment Plans (one line per item)" value={form.payment_plans_text} onChange={(e) => setForm((s) => ({ ...s, payment_plans_text: e.target.value }))} />
          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Documents (one line per item)" value={form.documents_text} onChange={(e) => setForm((s) => ({ ...s, documents_text: e.target.value }))} />
          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Gallery (one line per URL)" value={form.gallery_text} onChange={(e) => setForm((s) => ({ ...s, gallery_text: e.target.value }))} />
          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Videos (one line per URL)" value={form.videos_text} onChange={(e) => setForm((s) => ({ ...s, videos_text: e.target.value }))} />
          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Amenities (one per line)" value={form.amenities_text} onChange={(e) => setForm((s) => ({ ...s, amenities_text: e.target.value }))} />
          <textarea className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Nearby Landmarks (one per line)" value={form.nearby_landmarks_text} onChange={(e) => setForm((s) => ({ ...s, nearby_landmarks_text: e.target.value }))} />

          <button className="btn-primary px-4 py-2 md:col-span-2">Create Project</button>
        </form>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {(projects ?? []).map((project) => (
          <article key={project.id} className="card p-5">
            <h2 className="font-display text-xl text-ink">{project.name}</h2>
            <p className="text-steel mt-1">Developer: {project.developer_name}</p>
            <p className="text-steel">Partner: {project.sole_selling_partner ?? "-"}</p>
            <p className="text-steel">Location: {project.location}</p>
            <p className="mt-2 text-sm">Status: <span className="font-semibold">{project.project_status}</span></p>
            <p className="text-sm">Inventory: {project.sold_inventory}/{project.total_inventory} sold</p>
            <p className="text-sm">Available: <span className="font-semibold">{project.available_inventory}</span></p>
            <p className="text-sm text-steel mt-2">Legal: {project.legal_status ?? "-"}</p>
            <p className="text-sm text-steel">Amenities: {(project.amenities ?? []).slice(0, 3).join(", ") || "-"}</p>
            <p className="text-sm text-steel">Nearby: {(project.nearby_landmarks ?? []).slice(0, 3).join(", ") || "-"}</p>
            {project.google_maps_url ? <a className="text-cyan-300 underline text-sm mt-2 inline-block" href={project.google_maps_url} target="_blank" rel="noreferrer">Open Map</a> : null}
          </article>
        ))}
      </section>
    </div>
  );
}
