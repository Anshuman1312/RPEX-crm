import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "../services/api";
import NewBookingModal from "../sales/NewBookingModal";
import ComingSoonModal from "../components/ComingSoonModal";
import StatCard from "./components/stats-card";
import QuickAction from "./components/quick-action";
import { Icons } from "./components/icons";
import FinanceMetrics from "./components/finance-metrics";
import EmptyState from "./components/empty-state";

// --- UI Sub-Components ---

const COLORS = ["#10b981", "#f59e0b", "#3b82f6", "#ef4444", "#6366f1"];

export default function DashboardPage() {
  // Modal State
  const [isBookingOpen, setIsBookingOpen] = useState(false);
  const [isComingSoonOpen, setIsComingSoonOpen] = useState(false);
  const [comingSoonFeature, setComingSoonFeature] = useState("");
  const [activeAction, setActiveAction] = useState("");
  const [progression, setProgession] = useState([]);

  // Generic Quick Action Handler
  const handleQuickAction = (actionName: string) => {
    setActiveAction(actionName);
    switch (actionName) {
      case "New Booking":
        setIsBookingOpen(true);
        break;
      default:
        setComingSoonFeature(actionName);
        setIsComingSoonOpen(true);
        break;
    }
  };
  // Data Fetching
  const { data: metrics, isLoading } = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: async () => {
      const response = await api.get("/dashboard/overview");
      return response.data.data;
    },
    //refetchInterval: 30000,
  });

  // Chart Data Formatting
  const inventoryChartData = useMemo(
    () => [
      { name: "Available", value: metrics?.inventory?.available || 0 },
      { name: "Reserved", value: metrics?.inventory?.reserved || 0 },
      { name: "Sold", value: metrics?.inventory?.sold || 0 },
    ],
    [metrics],
  );

  const formatINR = (val: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(val);

  if (isLoading)
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500 font-medium animate-pulse">
            Analyzing Project Data...
          </p>
        </div>
      </div>
    );

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10">
      {/* Header Section */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Dashboard
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Unified view of Plotting Inventory & Sales Pipeline.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-white border border-slate-200 rounded-xl shadow-sm text-xs font-bold text-slate-600">
            Last Updated: {new Date().toLocaleTimeString()}
          </div>
          <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            System Live
          </span>
        </div>
      </header>

      {/* KPI Stats Row */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Inventory"
          value={metrics?.inventory?.total || 0}
          subtitle="Total project units"
          icon={Icons.Inventory}
          colorClass="text-blue-500"
        />
        <StatCard
          title="Available Plots"
          value={metrics?.inventory?.available || 0}
          subtitle="Open for sale"
          icon={Icons.Inventory}
          colorClass="text-emerald-500"
        />
        <StatCard
          title="Today's Leads"
          value={metrics?.leads?.today || 0}
          subtitle="New CRM inquiries"
          icon={Icons.Leads}
          colorClass="text-orange-500"
        />
        <StatCard
          title="Daily Collection"
          value={formatINR(metrics?.collections_today || 0)}
          subtitle="Payments received today"
          icon={Icons.Money}
          colorClass="text-cyan-600"
        />
      </section>

      {/* Analytics Center */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Inventory Distribution (Pie Chart) */}
        <div className="lg:col-span-4 bg-white border border-slate-100 rounded-3xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">
            Stock Distribution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={inventoryChartData}
                  innerRadius={70}
                  outerRadius={90}
                  paddingAngle={8}
                  dataKey="value"
                  cornerRadius={4}
                >
                  {inventoryChartData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-6 flex justify-around border-t border-slate-50 pt-6">
            {inventoryChartData.map((item, i) => (
              <div key={item.name} className="text-center">
                <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">
                  {item.name}
                </p>
                <p className="text-xl font-bold" style={{ color: COLORS[i] }}>
                  {item.value}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions & Pipeline Panel */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 rounded-3xl p-6 shadow-xl border border-slate-800">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                Command Center
              </h3>
              <span className="text-[10px] text-cyan-400 font-bold border border-cyan-400/30 px-2 py-0.5 rounded">
                Quick Actions
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <QuickAction
                label="New Lead"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "New Lead"}
                onClick={() => handleQuickAction("New Lead")}
              />
              <QuickAction
                label="Site Visit"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "Site Visit"}
                onClick={() => handleQuickAction("Site Visit")}
              />
              <QuickAction
                label="New Booking"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "New Booking"}
                onClick={() => handleQuickAction("New Booking")}
              />
              <QuickAction
                label="Add Payment"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "Add Payment"}
                onClick={() => handleQuickAction("Add Payment")}
              />
              <QuickAction
                label="Lead Report"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "Lead Report"}
                onClick={() => handleQuickAction("Lead Report")}
              />
              <QuickAction
                label="Expense"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "Expense"}
                onClick={() => handleQuickAction("Expense")}
              />
              <QuickAction
                label="Inventory"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "Inventory"}
                onClick={() => handleQuickAction("Inventory")}
              />
              <QuickAction
                label="HR Panel"
                color="bg-slate-800/50"
                textColor="text-slate-300"
                isActive={activeAction === "HR Panel"}
                onClick={() => handleQuickAction("HR Panel")}
              />
            </div>
          </div>

          <div className="bg-white border border-slate-100 rounded-2xl p-3 md:p-3.5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                Pipeline Progression
              </h3>
              <div className="p-1 bg-slate-50 rounded text-cyan-600">
                <Icons.Trends />
              </div>
            </div>
            {progression.length === 0 ? (
              <EmptyState
                title="No Active Pipeline Progression"
                description="Lead stage updates and pipeline metrics will appear here once activity begins."
                icon={<Icons.Trends />}
              />
            ) : (
              <div className="flex items-center gap-3">
                {progression.map((step: any, i: number) => (
                  <div
                    key={typeof step === "string" ? step : step.name || i}
                    className="flex-1 space-y-3"
                  >
                    <div
                      className={`h-2.5 w-full rounded-full ${i < 3 ? "bg-cyan-500 shadow-sm shadow-cyan-100" : "bg-slate-100"}`}
                    />
                    <span className="text-[9px] block text-center font-bold text-slate-500 uppercase tracking-tighter">
                      {typeof step === "string" ? step : step.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Finance Metrics */}
      <FinanceMetrics
        targetRevenue="₹0"
        targetAchievedPercent={0}
        totalOutstanding="₹0"
        pendingInstallmentsCount={0}
        siteVisitsMonthCount={0}
        visitorsAttendedPercent={0}
      />

      {/* Render Modals */}
      <NewBookingModal
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
      />
      <ComingSoonModal
        isOpen={isComingSoonOpen}
        onClose={() => setIsComingSoonOpen(false)}
        featureName={comingSoonFeature}
      />
    </div>
  );
}
// // import { useMemo } from "react";
// // import { useQuery } from "@tanstack/react-query";
// // import {
// //   Area,
// //   AreaChart,
// //   Bar,
// //   BarChart,
// //   CartesianGrid,
// //   Pie,
// //   PieChart,
// //   ResponsiveContainer,
// //   Tooltip,
// //   XAxis,
// //   YAxis
// // } from "recharts";

// // import { api } from "../services/api";

// // type DashboardMetrics = {
// //   total_leads: number;
// //   new_leads_today: number;
// //   site_visits_today: number;
// //   bookings: number;
// //   sales_value: number;
// //   revenue: number;
// //   marketing_spend: number;
// //   cpl: number;
// //   pending_followups: number;
// //   today_leads: number;
// //   converted_leads: number;
// //   pending_leads: number;
// //   conversion_rate: number;
// //   top_campaign: string | null;
// //   top_keyword: string | null;
// //   sales_team_performance: Array<{
// //     user_id: string;
// //     name: string;
// //     assigned_leads: number;
// //     converted_leads: number;
// //     bookings: number;
// //     sales_value: number;
// //     conversion_rate: number;
// //   }>;
// // };

// // function formatCurrency(value: number) {
// //   return new Intl.NumberFormat("en-IN", {
// //     style: "currency",
// //     currency: "INR",
// //     maximumFractionDigits: 0
// //   }).format(value || 0);
// // }

// // export default function DashboardPage() {
// //   const { data } = useQuery({
// //     queryKey: ["dashboard-metrics"],
// //     queryFn: async () => {
// //       const response = await api.get<DashboardMetrics>("/analytics/dashboard");
// //       return response.data;
// //     },
// //     refetchInterval: 15000
// //   });

// //   const chartData = useMemo(
// //     () => [
// //       { name: "Total", value: data?.total_leads ?? 0 },
// //       { name: "Today", value: data?.today_leads ?? 0 },
// //       { name: "Converted", value: data?.converted_leads ?? 0 },
// //       { name: "Pending", value: data?.pending_leads ?? 0 }
// //     ],
// //     [data]
// //   );

// //   const splitData = useMemo(
// //     () => [
// //       { name: "Converted", value: data?.converted_leads ?? 0 },
// //       { name: "Pending", value: data?.pending_leads ?? 0 }
// //     ],
// //     [data]
// //   );

// //   const performanceData = useMemo(
// //     () => (data?.sales_team_performance ?? []).slice(0, 8).map((row) => ({
// //       name: row.name,
// //       sales_value: Number(row.sales_value ?? 0),
// //       conversion_rate: Number(row.conversion_rate ?? 0)
// //     })),
// //     [data]
// //   );

// //   const metricCards: Array<[string, string | number]> = [
// //     ["Total Leads", data?.total_leads ?? 0],
// //     ["New Leads Today", data?.new_leads_today ?? 0],
// //     ["Site Visits Today", data?.site_visits_today ?? 0],
// //     ["Bookings", data?.bookings ?? 0],
// //     ["Sales Value", formatCurrency(data?.sales_value ?? 0)],
// //     ["Revenue", formatCurrency(data?.revenue ?? 0)],
// //     ["Marketing Spend", formatCurrency(data?.marketing_spend ?? 0)],
// //     ["Cost Per Lead (CPL)", formatCurrency(data?.cpl ?? 0)],
// //     ["Conversion Rate", `${data?.conversion_rate ?? 0}%`],
// //     ["Pending Follow-ups", data?.pending_followups ?? 0]
// //   ];

// //   return (
// //     <div className="space-y-6">
// //       <div className="card p-6">
// //         <h1 className="font-display text-3xl text-ink">Operations Dashboard</h1>
// //         <p className="text-steel mt-2">Real-time visibility for lead flow, campaign health, and conversion momentum.</p>
// //       </div>

// //       <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
// //         {metricCards.map(([label, value]) => (
// //           <article key={String(label)} className="card p-5">
// //             <p className="text-steel text-sm">{label}</p>
// //             <p className="font-display text-3xl mt-2 text-ink">{value}</p>
// //           </article>
// //         ))}
// //       </div>

// //       <section className="grid gap-6 xl:grid-cols-3">
// //         <div className="card p-6 xl:col-span-2">
// //         <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
// //           <h2 className="font-display text-2xl text-ink">Lead Velocity</h2>
// //           <div className="text-sm text-steel">
// //             Top campaign: <span className="font-semibold text-ink">{data?.top_campaign ?? "N/A"}</span>
// //           </div>
// //         </div>
// //         <div className="h-64 sm:h-72">
// //           <ResponsiveContainer width="100%" height="100%">
// //             <AreaChart data={chartData}>
// //               <CartesianGrid strokeDasharray="3 3" />
// //               <XAxis dataKey="name" />
// //               <YAxis />
// //               <Tooltip />
// //               <Area type="monotone" dataKey="value" stroke="#0ea5a4" fill="#99f6e4" />
// //             </AreaChart>
// //           </ResponsiveContainer>
// //         </div>
// //         </div>

// //         <div className="card p-6">
// //           <h2 className="font-display text-2xl text-ink">Conversion Split</h2>
// //           <div className="h-64 sm:h-72 mt-3">
// //             <ResponsiveContainer width="100%" height="100%">
// //               <PieChart>
// //                 <Pie data={splitData} dataKey="value" nameKey="name" outerRadius={95} fill="#0ea5a4" label />
// //                 <Tooltip />
// //               </PieChart>
// //             </ResponsiveContainer>
// //           </div>
// //         </div>
// //       </section>

// //       <section className="card p-6">
// //         <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
// //           <h2 className="font-display text-2xl text-ink">Pipeline Compare</h2>
// //           <div className="text-sm text-steel">
// //             Top keyword: <span className="font-semibold text-ink">{data?.top_keyword ?? "N/A"}</span>
// //           </div>
// //         </div>
// //         <div className="h-56 sm:h-64">
// //           <ResponsiveContainer width="100%" height="100%">
// //             <BarChart data={chartData}>
// //               <CartesianGrid strokeDasharray="3 3" />
// //               <XAxis dataKey="name" />
// //               <YAxis />
// //               <Tooltip />
// //               <Bar dataKey="value" fill="#f59e0b" radius={[8, 8, 0, 0]} />
// //             </BarChart>
// //           </ResponsiveContainer>
// //         </div>
// //       </section>

// //       <section className="grid gap-6 xl:grid-cols-3">
// //         <div className="card p-6 xl:col-span-2">
// //           <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
// //             <h2 className="font-display text-2xl text-ink">Sales Team Performance</h2>
// //             <p className="text-sm text-steel">Ranked by sales value and conversions</p>
// //           </div>
// //           <div className="h-64 sm:h-72">
// //             <ResponsiveContainer width="100%" height="100%">
// //               <BarChart data={performanceData}>
// //                 <CartesianGrid strokeDasharray="3 3" />
// //                 <XAxis dataKey="name" />
// //                 <YAxis />
// //                 <Tooltip />
// //                 <Bar dataKey="sales_value" fill="#0ea5a4" radius={[8, 8, 0, 0]} />
// //               </BarChart>
// //             </ResponsiveContainer>
// //           </div>
// //         </div>

// //         <div className="card p-6">
// //           <h2 className="font-display text-2xl text-ink">Top Contributors</h2>
// //           <div className="mt-4 space-y-3 text-sm">
// //             {(data?.sales_team_performance ?? []).slice(0, 6).map((row) => (
// //               <div key={row.user_id} className="rounded-xl border border-slate-100 p-3">
// //                 <p className="font-semibold text-ink">{row.name}</p>
// //                 <p className="text-steel">Assigned: {row.assigned_leads} | Converted: {row.converted_leads}</p>
// //                 <p className="text-steel">Bookings: {row.bookings} | Sales: {formatCurrency(row.sales_value)}</p>
// //               </div>
// //             ))}
// //             {(data?.sales_team_performance ?? []).length === 0 ? <p className="text-steel">No team performance data yet.</p> : null}
// //           </div>
// //         </div>
// //       </section>
// //     </div>
// //   );
// // }

// import { useMemo } from "react";
// import { useQuery } from "@tanstack/react-query";
// import {
//   Area, AreaChart, Bar, BarChart, CartesianGrid,
//   Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis
// } from "recharts";
// import { api } from "../services/api";

// // --- Helper Components & Styles ---

// const COLORS = ["#10b981", "#f59e0b", "#3b82f6", "#ef4444", "#6366f1"];

// const StatCard = ({ title, value, subtitle, icon: Icon, colorClass = "text-cyan-500" }: any) => (
//   <div className="card p-5 flex items-start justify-between group hover:border-cyan-500/50 transition-all cursor-default">
//     <div>
//       <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">{title}</p>
//       <p className="font-display text-2xl mt-2 text-slate-900">{value}</p>
//       {subtitle && <p className="text-slate-400 text-xs mt-1">{subtitle}</p>}
//     </div>
//     <div className={`p-3 rounded-xl bg-slate-50 ${colorClass} group-hover:scale-110 transition-transform`}>
//       <Icon />
//     </div>
//   </div>
// );

// const QuickAction = ({ label, onClick, color = "bg-white" }: any) => (
//   <button
//     onClick={onClick}
//     className={`${color} border border-slate-200 hover:border-cyan-500 hover:shadow-md transition-all p-4 rounded-2xl text-center group`}
//   >
//     <p className="text-sm font-semibold text-slate-700 group-hover:text-cyan-600">{label}</p>
//   </button>
// );

// // --- Icons (Inline SVGs for high performance) ---
// const Icons = {
//   Inventory: () => (
//     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
//   ),
//   Leads: () => (
//     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
//   ),
//   Money: () => (
//     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
//   ),
//   Trends: () => (
//     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
//   )
// };

// export default function DashboardPage() {
//   const { data: metrics, isLoading } = useQuery({
//     queryKey: ["dashboard-overview"],
//     queryFn: async () => {
//       const response = await api.get("/dashboard/overview");
//       return response.data.data;
//     },
//     refetchInterval: 30000 // Refresh every 30 seconds
//   });

//   const inventoryChartData = useMemo(() => [
//     { name: "Available", value: metrics?.inventory?.available || 0 },
//     { name: "Reserved", value: metrics?.inventory?.reserved || 0 },
//     { name: "Sold", value: metrics?.inventory?.sold || 0 }
//   ], [metrics]);

//   const formatINR = (val: number) =>
//     new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(val);

//   if (isLoading) return <div className="p-10 animate-pulse text-slate-400">Loading Intelligence...</div>;

//   return (
//     <div className="max-w-[1600px] mx-auto space-y-8 animate-in fade-in duration-500">

//       {/* Header Section */}
//       <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
//         <div>
//           <h1 className="text-4xl font-display font-bold text-slate-900 tracking-tight">Sanskruti City Overview</h1>
//           <p className="text-slate-500 mt-1">Real-time performance metrics for Plotting Projects.</p>
//         </div>
//         <div className="flex gap-2">
//           <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full flex items-center gap-1">
//             <span className="w-2 h-2 bg-emerald-500 rounded-full animate-ping" />
//             Live System
//           </span>
//         </div>
//       </header>

//       {/* Primary KPI Grid */}
//       <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
//         <StatCard title="Total Inventory" value={metrics?.inventory?.total || 0} subtitle="Active Plots" icon={Icons.Inventory} colorClass="text-blue-500" />
//         <StatCard title="Available Plots" value={metrics?.inventory?.available || 0} subtitle="Ready for Booking" icon={Icons.Inventory} colorClass="text-emerald-500" />
//         <StatCard title="Today's Leads" value={metrics?.leads?.today || 0} subtitle="New Inquiries" icon={Icons.Leads} colorClass="text-orange-500" />
//         <StatCard title="Total Collection" value={formatINR(metrics?.collections_today || 0)} subtitle="Received Today" icon={Icons.Money} colorClass="text-cyan-600" />
//       </section>

//       {/* Main Analysis Section */}
//       <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

//         {/* Plot Inventory Chart */}
//         <div className="lg:col-span-4 card p-6">
//           <h3 className="font-display text-lg font-bold text-slate-800 mb-6">Inventory Status</h3>
//           <div className="h-64">
//             <ResponsiveContainer width="100%" height="100%">
//               <PieChart>
//                 <Pie
//                     data={inventoryChartData}
//                     innerRadius={60}
//                     outerRadius={80}
//                     paddingAngle={5}
//                     dataKey="value"
//                 >
//                   {inventoryChartData.map((_, index) => (
//                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                   ))}
//                 </Pie>
//                 <Tooltip />
//               </PieChart>
//             </ResponsiveContainer>
//           </div>
//           <div className="mt-4 grid grid-cols-3 gap-2">
//             {inventoryChartData.map((item, i) => (
//               <div key={item.name} className="text-center">
//                 <p className="text-[10px] uppercase font-bold text-slate-400">{item.name}</p>
//                 <p className="text-lg font-display font-bold" style={{ color: COLORS[i] }}>{item.value}</p>
//               </div>
//             ))}
//           </div>
//         </div>

//         {/* Quick Actions Panel */}
//         <div className="lg:col-span-8 flex flex-col gap-6">
//           <div className="card p-6 flex-1 bg-slate-900 border-none">
//             <h3 className="font-display text-lg font-bold text-white mb-4">Quick Management</h3>
//             <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
//               <QuickAction label="Add Lead" color="bg-slate-800" />
//               <QuickAction label="Add Customer" color="bg-slate-800" />
//               <QuickAction label="Schedule Visit" color="bg-slate-800" />
//               <QuickAction label="New Booking" color="bg-cyan-500 border-none !text-white" />
//               <QuickAction label="Add Payment" color="bg-slate-800" />
//               <QuickAction label="Invoice" color="bg-slate-800" />
//               <QuickAction label="Upload Doc" color="bg-slate-800" />
//               <QuickAction label="Reports" color="bg-slate-800" />
//             </div>
//           </div>

//           <div className="card p-6 flex-1">
//              <div className="flex items-center justify-between mb-4">
//                 <h3 className="font-display text-lg font-bold text-slate-800">Pipeline Health</h3>
//                 <Icons.Trends />
//              </div>
//              <div className="flex items-center gap-2">
//                 {['Lead', 'Visit', 'Negotiation', 'Booking', 'Registered'].map((step, i) => (
//                   <div key={step} className="flex-1 flex flex-col items-center gap-2">
//                     <div className={`h-2 w-full rounded-full ${i < 3 ? 'bg-cyan-500' : 'bg-slate-200'}`} />
//                     <span className="text-[10px] font-bold text-slate-500 uppercase">{step}</span>
//                   </div>
//                 ))}
//              </div>
//           </div>
//         </div>
//       </div>

//       {/* Finance & Outstanding Section */}
//       <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//           <div className="card p-6 bg-gradient-to-br from-indigo-500 to-purple-600 text-white border-none">
//              <p className="text-sm font-bold opacity-80 uppercase tracking-widest">Project Profit</p>
//              <h2 className="text-4xl font-display font-bold mt-2">₹4.2 Cr</h2>
//              <div className="mt-4 p-3 bg-white/10 rounded-xl text-xs">
//                 Target: ₹10 Cr | <span className="text-emerald-300 font-bold">42% achieved</span>
//              </div>
//           </div>

//           <div className="card p-6">
//              <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">Outstanding Amount</p>
//              <h2 className="text-3xl font-display font-bold text-red-500 mt-2">₹84.50 L</h2>
//              <div className="mt-4 flex items-center justify-between text-xs font-semibold">
//                 <span className="text-slate-400">12 Pending Payments</span>
//                 <button className="text-cyan-600 hover:underline">View Ledger</button>
//              </div>
//           </div>

//           <div className="card p-6">
//              <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">Site Visits (Monthly)</p>
//              <h2 className="text-3xl font-display font-bold text-slate-900 mt-2">142</h2>
//              <div className="mt-4 h-2 bg-slate-100 rounded-full overflow-hidden">
//                 <div className="h-full bg-emerald-500 w-[70%]" />
//              </div>
//              <p className="text-[10px] text-slate-400 mt-2 font-bold uppercase">70% Attendance Rate</p>
//           </div>
//       </section>

//     </div>
//   );
// }
