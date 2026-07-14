import { useMutation } from "@tanstack/react-query";

import { api } from "../services/api";

export default function ReportsPage() {
  const scheduleDaily = useMutation({ mutationFn: async () => (await api.post("/reports/schedule/daily")).data });
  const scheduleWeekly = useMutation({ mutationFn: async () => (await api.post("/reports/schedule/weekly")).data });

  async function exportLeads() {
    const response = await api.get("/reports/export/leads", { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "leads_report.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  return (
    <div className="space-y-6">
      <section className="card p-6">
        <h1 className="font-display text-3xl text-ink">Reporting Studio</h1>
        <p className="text-steel mt-2">Schedule recurring exports and trigger on-demand reporting actions.</p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn-primary px-4 py-3" onClick={exportLeads}>
            Export Leads CSV
          </button>
          <button
            className="btn-accent px-4 py-3"
            onClick={() => scheduleDaily.mutate()}
          >
            Queue Daily Report
          </button>
          <button
            className="btn-warm px-4 py-3"
            onClick={() => scheduleWeekly.mutate()}
          >
            Queue Weekly Report
          </button>
        </div>

        <div className="mt-4 text-sm text-steel space-y-1">
          {scheduleDaily.data ? <p>Daily task id: {scheduleDaily.data.task_id}</p> : null}
          {scheduleWeekly.data ? <p>Weekly task id: {scheduleWeekly.data.task_id}</p> : null}
        </div>
      </section>
    </div>
  );
}
