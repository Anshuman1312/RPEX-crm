import { useQuery } from "@tanstack/react-query";

import { fetchPartnerBookings, fetchPartnerCustomers, fetchPartnerDashboard, fetchPartnerDocuments, fetchPartnerPayments } from "../services/crm";

export default function PartnerPortalPage() {
  const { data: dashboard } = useQuery({ queryKey: ["partner-dashboard"], queryFn: fetchPartnerDashboard });
  const { data: customers } = useQuery({ queryKey: ["partner-customers"], queryFn: fetchPartnerCustomers });
  const { data: bookings } = useQuery({ queryKey: ["partner-bookings"], queryFn: fetchPartnerBookings });
  const { data: payments } = useQuery({ queryKey: ["partner-payments"], queryFn: fetchPartnerPayments });
  const { data: documents } = useQuery({ queryKey: ["partner-documents"], queryFn: fetchPartnerDocuments });

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-cyan-300">Partner Access</p>
            <h1 className="font-display text-3xl text-ink">Channel Partner Portal</h1>
            <p className="text-steel mt-2">View only your mapped customers, bookings, collections, and documents.</p>
          </div>
          <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">
            RPEX Partner Hub
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <article className="card p-4"><p className="text-xs text-steel">Customers</p><p className="text-2xl font-display text-ink">{dashboard?.customers ?? 0}</p></article>
        <article className="card p-4"><p className="text-xs text-steel">Bookings</p><p className="text-2xl font-display text-ink">{dashboard?.bookings ?? 0}</p></article>
        <article className="card p-4"><p className="text-xs text-steel">Payments</p><p className="text-2xl font-display text-ink">{dashboard?.payments ?? 0}</p></article>
        <article className="card p-4"><p className="text-xs text-steel">Documents</p><p className="text-2xl font-display text-ink">{dashboard?.documents ?? 0}</p></article>
        <article className="card p-4"><p className="text-xs text-steel">Booking Value</p><p className="text-2xl font-display text-ink">{dashboard?.total_booking_value ?? 0}</p></article>
        <article className="card p-4"><p className="text-xs text-steel">Collections</p><p className="text-2xl font-display text-ink">{dashboard?.total_collections ?? 0}</p></article>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="card p-5">
          <h2 className="font-display text-lg text-ink">My Customers</h2>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(customers ?? []).slice(0, 6).map((row) => <div key={row.id} className="rounded-lg border border-slate-100 p-2">{row.full_name} | {row.phone}</div>)}
          </div>
        </article>
        <article className="card p-5">
          <h2 className="font-display text-lg text-ink">My Bookings</h2>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(bookings ?? []).slice(0, 6).map((row) => <div key={row.id} className="rounded-lg border border-slate-100 p-2">{row.project_name} | {row.booking_value}</div>)}
          </div>
        </article>
        <article className="card p-5">
          <h2 className="font-display text-lg text-ink">My Payments</h2>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(payments ?? []).slice(0, 6).map((row) => <div key={row.id} className="rounded-lg border border-slate-100 p-2">{row.amount} | {row.status}</div>)}
          </div>
        </article>
        <article className="card p-5">
          <h2 className="font-display text-lg text-ink">My Documents</h2>
          <div className="mt-3 space-y-2 text-sm text-steel">
            {(documents ?? []).slice(0, 6).map((row) => (
              <div key={row.id} className="rounded-lg border border-slate-100 p-2">
                {row.category} | {row.file_name}
                {row.signed_url ? (
                  <a className="ml-2 text-cyan-300 underline" href={row.signed_url} target="_blank" rel="noreferrer">
                    View
                  </a>
                ) : null}
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
