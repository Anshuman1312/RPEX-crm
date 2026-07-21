// import { FormEvent, useMemo, useState } from "react";
// import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// import { createInventoryUnit, fetchInventoryUnits, fetchProjects } from "../services/crm";

// const STATUS_META = {
//   AVAILABLE: { emoji: "🟢", label: "Available", badge: "bg-emerald-100 text-emerald-800" },
//   HOLD: { emoji: "🟡", label: "Hold", badge: "bg-amber-100 text-amber-800" },
//   BOOKED: { emoji: "🔵", label: "Booked", badge: "bg-sky-100 text-sky-800" },
//   SOLD: { emoji: "🔴", label: "Sold", badge: "bg-rose-100 text-rose-800" }
// } as const;

// export default function InventoryPage() {
//   const queryClient = useQueryClient();
//   const [form, setForm] = useState({
//     project_id: "",
//     plot_no: "",
//     size: "",
//     facing: "",
//     is_corner: false,
//     price: 0,
//     booking_status: "AVAILABLE" as "AVAILABLE" | "HOLD" | "BOOKED" | "SOLD",
//     customer_name: "",
//     sales_executive: "",
//     booking_date: "",
//     agreement_status: "PENDING",
//     payment_status: "PENDING"
//   });

//   const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: fetchProjects });
//   const { data: units, isLoading } = useQuery({
//     queryKey: ["inventory", form.project_id || "all"],
//     queryFn: () => fetchInventoryUnits(form.project_id || undefined)
//   });

//   const createMutation = useMutation({
//     mutationFn: createInventoryUnit,
//     onSuccess: () => {
//       queryClient.invalidateQueries({ queryKey: ["inventory"] });
//       setForm((current) => ({
//         ...current,
//         plot_no: "",
//         size: "",
//         facing: "",
//         is_corner: false,
//         price: 0,
//         booking_status: "AVAILABLE",
//         customer_name: "",
//         sales_executive: "",
//         booking_date: "",
//         agreement_status: "PENDING",
//         payment_status: "PENDING"
//       }));
//     }
//   });

//   const selectedProjectName = useMemo(
//     () => projects?.find((project) => project.id === form.project_id)?.name ?? "Select Project",
//     [projects, form.project_id]
//   );

//   function handleSubmit(event: FormEvent) {
//     event.preventDefault();
//     createMutation.mutate({
//       project_id: form.project_id,
//       plot_no: form.plot_no,
//       size: form.size,
//       facing: form.facing || null,
//       is_corner: form.is_corner,
//       price: Number(form.price),
//       booking_status: form.booking_status,
//       customer_name: form.customer_name || null,
//       sales_executive: form.sales_executive || null,
//       booking_date: form.booking_date || null,
//       agreement_status: form.agreement_status || null,
//       payment_status: form.payment_status || null
//     });
//   }

//   return (
//     <div className="space-y-6">
//       <section className="card p-6">
//         <h1 className="font-display text-3xl text-ink">Inventory Management</h1>
//         <p className="text-steel mt-2">Track plot and flat availability with booking, agreement, and payment status.</p>

//         <form onSubmit={handleSubmit} className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3">
//           <select className="rounded-xl border border-slate-200 px-3 py-2 md:col-span-2" value={form.project_id} onChange={(e) => setForm((s) => ({ ...s, project_id: e.target.value }))} required>
//             <option value="">Select Project</option>
//             {(projects ?? []).map((project) => (
//               <option key={project.id} value={project.id}>{project.name}</option>
//             ))}
//           </select>
//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Plot No" value={form.plot_no} onChange={(e) => setForm((s) => ({ ...s, plot_no: e.target.value }))} required />
//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Size (e.g. 1200 sqft)" value={form.size} onChange={(e) => setForm((s) => ({ ...s, size: e.target.value }))} required />

//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Facing" value={form.facing} onChange={(e) => setForm((s) => ({ ...s, facing: e.target.value }))} />
//           <label className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-steel">
//             <input type="checkbox" checked={form.is_corner} onChange={(e) => setForm((s) => ({ ...s, is_corner: e.target.checked }))} />
//             Corner Unit
//           </label>
//           <input className="rounded-xl border border-slate-200 px-3 py-2" type="number" min={0} placeholder="Price" value={form.price} onChange={(e) => setForm((s) => ({ ...s, price: Number(e.target.value) }))} required />

//           <select className="rounded-xl border border-slate-200 px-3 py-2" value={form.booking_status} onChange={(e) => setForm((s) => ({ ...s, booking_status: e.target.value as "AVAILABLE" | "HOLD" | "BOOKED" | "SOLD" }))}>
//             <option value="AVAILABLE">🟢 Available</option>
//             <option value="HOLD">🟡 Hold</option>
//             <option value="BOOKED">🔵 Booked</option>
//             <option value="SOLD">🔴 Sold</option>
//           </select>

//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Customer Name" value={form.customer_name} onChange={(e) => setForm((s) => ({ ...s, customer_name: e.target.value }))} />
//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Sales Executive" value={form.sales_executive} onChange={(e) => setForm((s) => ({ ...s, sales_executive: e.target.value }))} />
//           <input className="rounded-xl border border-slate-200 px-3 py-2" type="date" value={form.booking_date} onChange={(e) => setForm((s) => ({ ...s, booking_date: e.target.value }))} />
//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Agreement Status" value={form.agreement_status} onChange={(e) => setForm((s) => ({ ...s, agreement_status: e.target.value }))} />
//           <input className="rounded-xl border border-slate-200 px-3 py-2" placeholder="Payment Status" value={form.payment_status} onChange={(e) => setForm((s) => ({ ...s, payment_status: e.target.value }))} />

//           <button className="btn-primary px-4 py-2 md:col-span-4">Add Inventory Unit to {selectedProjectName}</button>
//         </form>
//       </section>

//       <section className="card overflow-hidden">
//         <div className="overflow-x-auto">
//           <table className="responsive-table w-full text-sm">
//             <thead className="bg-slate-50 text-slate-600">
//               <tr>
//                 <th className="text-left px-4 py-3">Plot No</th>
//                 <th className="text-left px-4 py-3">Size</th>
//                 <th className="text-left px-4 py-3">Facing</th>
//                 <th className="text-left px-4 py-3">Corner/Normal</th>
//                 <th className="text-left px-4 py-3">Price</th>
//                 <th className="text-left px-4 py-3">Booking Status</th>
//                 <th className="text-left px-4 py-3">Customer</th>
//                 <th className="text-left px-4 py-3">Sales Executive</th>
//                 <th className="text-left px-4 py-3">Booking Date</th>
//                 <th className="text-left px-4 py-3">Agreement</th>
//                 <th className="text-left px-4 py-3">Payment</th>
//               </tr>
//             </thead>
//             <tbody>
//               {isLoading ? (
//                 <tr><td className="px-4 py-4" colSpan={11}>Loading inventory...</td></tr>
//               ) : (
//                 (units ?? []).map((unit) => {
//                   const meta = STATUS_META[unit.booking_status];
//                   return (
//                     <tr key={unit.id} className="border-t border-slate-100">
//                       <td className="px-4 py-3 font-semibold text-ink" data-label="Plot No">{unit.plot_no}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Size">{unit.size}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Facing">{unit.facing ?? "-"}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Corner/Normal">{unit.corner_or_normal}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Price">{unit.price}</td>
//                       <td className="px-4 py-3" data-label="Booking Status">
//                         <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${meta.badge}`}>
//                           <span>{meta.emoji}</span>
//                           <span>{meta.label}</span>
//                         </span>
//                       </td>
//                       <td className="px-4 py-3 text-steel" data-label="Customer">{unit.customer_name ?? "-"}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Sales Executive">{unit.sales_executive ?? "-"}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Booking Date">{unit.booking_date ?? "-"}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Agreement">{unit.agreement_status ?? "-"}</td>
//                       <td className="px-4 py-3 text-steel" data-label="Payment">{unit.payment_status ?? "-"}</td>
//                     </tr>
//                   );
//                 })
//               )}
//             </tbody>
//           </table>
//         </div>
//       </section>
//     </div>
//   );
// }


import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../services/api";

const STATUS_COLORS: Record<string, string> = {
  AVAILABLE: "bg-emerald-500 hover:bg-emerald-600",
  BLOCKED: "bg-amber-500 hover:bg-amber-600",
  BOOKED: "bg-rose-500 hover:bg-rose-600",
  REGISTERED: "bg-indigo-600 hover:bg-indigo-700",
  CANCELLED: "bg-slate-400 hover:bg-slate-500",
};

export default function InventoryPage() {
  const [filter, setFilter] = useState("ALL");

  const { data: units, isLoading } = useQuery({
    queryKey: ["inventory-units"],
    queryFn: async () => {
      const res = await api.get("/inventory");
      return res.data;
    }
  });

  const filteredUnits = units?.filter((u: any) => filter === "ALL" || u.booking_status === filter);

  return (
    <div className="space-y-6">
      {/* Header & Legend */}
      <section className="card p-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold text-slate-900">Plot Inventory</h1>
          <p className="text-slate-500">Sanskruti City Layout Plan & Status</p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          {Object.entries(STATUS_COLORS).map(([status, color]) => (
            <button 
                key={status}
                onClick={() => setFilter(status)}
                className={`px-3 py-1.5 rounded-full text-[10px] font-bold text-white transition-all ${color} ${filter === status ? 'ring-4 ring-slate-200' : 'opacity-80'}`}
            >
              {status}
            </button>
          ))}
          <button onClick={() => setFilter("ALL")} className="px-3 py-1.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600">ALL</button>
        </div>
      </section>

      {/* Visual Grid */}
      <section className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-3">
        {isLoading ? (
          <div className="col-span-full py-20 text-center text-slate-400 animate-pulse">Loading Layout...</div>
        ) : (
          filteredUnits?.map((unit: any) => (
            <div 
              key={unit.id}
              className={`relative aspect-square rounded-2xl p-3 text-white shadow-sm transition-all cursor-pointer group ${STATUS_COLORS[unit.booking_status] || 'bg-slate-200'}`}
            >
              <div className="flex justify-between items-start">
                <span className="text-lg font-display font-black">{unit.plot_no}</span>
                {unit.is_corner && (
                  <span className="w-2 h-2 bg-white rounded-full animate-pulse shadow-lg" title="Corner Plot" />
                )}
              </div>
              
              <div className="mt-auto">
                <p className="text-[10px] font-bold opacity-80 uppercase tracking-tighter">{unit.size} sqft</p>
                <p className="text-[9px] font-medium opacity-70">{unit.facing} Facing</p>
              </div>

              {/* Hover Tooltip */}
              <div className="absolute inset-0 bg-slate-900/90 rounded-2xl p-3 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-center text-[10px] z-10">
                 <p className="font-bold border-b border-slate-700 pb-1 mb-1">Plot Details</p>
                 <p>Price: ₹{unit.price}</p>
                 <p>PLC: ₹{unit.plc_charges || 0}</p>
                 <p>Status: {unit.booking_status}</p>
                 {unit.customer_name && <p className="mt-1 text-cyan-400">Sold to: {unit.customer_name}</p>}
              </div>
            </div>
          ))
        )}
      </section>

      {/* Summary Table for detailed view */}
      <section className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold tracking-widest">
            <tr>
              <th className="px-6 py-4">Plot No</th>
              <th className="px-6 py-4">Size</th>
              <th className="px-6 py-4">Facing</th>
              <th className="px-6 py-4">Attributes</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredUnits?.map((unit: any) => (
              <tr key={unit.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-6 py-4 font-bold text-slate-900">Plot {unit.plot_no}</td>
                <td className="px-6 py-4 text-slate-500">{unit.size} sqft</td>
                <td className="px-6 py-4 text-slate-500">{unit.facing || 'N/A'}</td>
                <td className="px-6 py-4">
                  <div className="flex gap-1">
                    {unit.is_corner && <span className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-[9px] font-bold">CORNER</span>}
                    {unit.plc_charges > 0 && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-[9px] font-bold">PLC APPLIED</span>}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase ${
                    unit.booking_status === 'AVAILABLE' ? 'text-emerald-600 bg-emerald-50' : 'text-rose-600 bg-rose-50'
                  }`}>
                    {unit.booking_status}
                  </span>
                </td>
                <td className="px-6 py-4 text-cyan-600 font-bold cursor-pointer hover:underline">View Details</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}