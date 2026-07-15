import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchDocumentSignedUrl, fetchDocuments, uploadDocument } from "../services/crm";

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [category, setCategory] = useState("agreement");
  const [customerId, setCustomerId] = useState("");
  const [bookingId, setBookingId] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const { data, isLoading } = useQuery({ queryKey: ["documents"], queryFn: fetchDocuments });

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setFile(null);
    }
  });

  const signedUrlMutation = useMutation({
    mutationFn: fetchDocumentSignedUrl,
    onSuccess: (data) => {
      if (data.signed_url) {
        window.open(data.signed_url, "_blank", "noopener,noreferrer");
      }
    }
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      return;
    }
    uploadMutation.mutate({
      file,
      category,
      customer_id: customerId || null,
      booking_id: bookingId || null
    });
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Documents</h1>
        <p className="text-steel mt-2">Upload customer files to Cloudinary and track metadata.</p>

        <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-3">
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Category (aadhaar, pan, agreement...)" value={category} onChange={(e) => setCategory(e.target.value)} required />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer ID (optional)" value={customerId} onChange={(e) => setCustomerId(e.target.value)} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Booking ID (optional)" value={bookingId} onChange={(e) => setBookingId(e.target.value)} />
          <input className="rounded-xl border border-slate-200 px-3 py-2" type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required />
          <button className="btn-primary px-4 py-2 md:col-span-2">Upload Document</button>
        </form>
      </section>

      <section className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="responsive-table w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left px-4 py-3">File</th>
                <th className="text-left px-4 py-3">Category</th>
                <th className="text-left px-4 py-3">Link</th>
                <th className="text-left px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td className="px-4 py-4" colSpan={4}>Loading documents...</td></tr>
              ) : (
                (data ?? []).map((row) => (
                  <tr key={row.id} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-semibold text-ink" data-label="File">{row.file_name}</td>
                    <td className="px-4 py-3 text-steel" data-label="Category">{row.category}</td>
                    <td className="px-4 py-3 text-steel" data-label="Link">{row.signed_url ? "Available" : row.storage_key}</td>
                    <td className="px-4 py-3" data-label="Action">
                      <button className="btn-secondary px-3 py-1 text-xs" onClick={() => signedUrlMutation.mutate(row.id)}>
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
