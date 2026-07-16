import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useDispatch, useSelector } from "react-redux";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { fetchCurrentUserProfile } from "../services/auth";
import { clearTokens } from "../auth/authSlice";
import { api } from "../services/api";
import { RootState } from "../store";

type MenuItem = {
  label: string;
  path: string;
  group: "crm" | "partner";
  roles: Array<
    | "ADMIN"
    | "SEO_MANAGER"
    | "SALES"
    | "ANALYST"
    | "SUPER_ADMIN"
    | "DIRECTOR"
    | "PROJECT_HEAD"
    | "MARKETING_MANAGER"
    | "SALES_MANAGER"
    | "SALES_EXECUTIVE"
    | "TELECALLER"
    | "CRM_EXECUTIVE"
    | "FINANCE"
    | "LEGAL"
    | "HR"
    | "RECEPTIONIST"
    | "CHANNEL_PARTNER"
    | "DEVELOPER"
    | "CUSTOMER_PORTAL"
  >;
};

const MENU_ITEMS: MenuItem[] = [
  { label: "Dashboard", path: "/dashboard", group: "crm", roles: ["ADMIN", "SEO_MANAGER", "SALES", "ANALYST", "SUPER_ADMIN", "DIRECTOR", "PROJECT_HEAD"] },
  { label: "Leads", path: "/leads", group: "crm", roles: ["ADMIN", "SEO_MANAGER", "SALES", "ANALYST", "SUPER_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE", "TELECALLER", "CRM_EXECUTIVE", "RECEPTIONIST"] },
  { label: "Campaigns", path: "/campaigns", group: "crm", roles: ["ADMIN", "SEO_MANAGER", "SUPER_ADMIN", "MARKETING_MANAGER"] },
  { label: "Projects", path: "/projects", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "DIRECTOR", "PROJECT_HEAD", "MARKETING_MANAGER", "SALES_MANAGER", "CRM_EXECUTIVE"] },
  { label: "Inventory", path: "/inventory", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "DIRECTOR", "PROJECT_HEAD", "MARKETING_MANAGER", "SALES_MANAGER", "SALES_EXECUTIVE", "CRM_EXECUTIVE"] },
  { label: "Keywords", path: "/keywords", group: "crm", roles: ["ADMIN", "SEO_MANAGER", "ANALYST", "SUPER_ADMIN", "MARKETING_MANAGER"] },
  { label: "Follow-ups", path: "/followups", group: "crm", roles: ["ADMIN", "SALES", "SUPER_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE", "TELECALLER"] },
  { label: "Telecalling", path: "/telecalling", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "TELECALLER", "SALES_MANAGER", "CRM_EXECUTIVE"] },
  { label: "Customers", path: "/customers", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "CRM_EXECUTIVE", "SALES_MANAGER", "RECEPTIONIST"] },
  { label: "Sales", path: "/sales", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE", "PROJECT_HEAD", "DIRECTOR"] },
  { label: "Sales Team", path: "/sales-team", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "SALES_MANAGER", "DIRECTOR", "PROJECT_HEAD"] },
  { label: "Site Visits", path: "/site-visits", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE", "PROJECT_HEAD", "DIRECTOR", "CRM_EXECUTIVE"] },
  { label: "Finance", path: "/finance", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "FINANCE", "DIRECTOR"] },
  { label: "Documents", path: "/documents", group: "crm", roles: ["ADMIN", "SUPER_ADMIN", "LEGAL", "CRM_EXECUTIVE"] },
  { label: "Reports", path: "/reports", group: "crm", roles: ["ADMIN", "ANALYST", "SUPER_ADMIN", "DIRECTOR", "FINANCE", "HR"] },
  { label: "Partner Portal", path: "/partner", group: "partner", roles: ["CHANNEL_PARTNER", "CUSTOMER_PORTAL", "ADMIN", "SUPER_ADMIN"] }
];

export function AppShell() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { role, refreshToken } = useSelector((state: RootState) => state.auth);
  const { data: profile } = useQuery({ queryKey: ["current-user-profile"], queryFn: fetchCurrentUserProfile });
  const [menuOpen, setMenuOpen] = useState(false);

  const menu = useMemo(
    () => {
      if (role === "ADMIN" || role === "SUPER_ADMIN") {
        return MENU_ITEMS;
      }

      return MENU_ITEMS.filter((item) => (role ? item.roles.includes(role) : false));
    },
    [role]
  );
  const crmMenu = menu.filter((item) => item.group === "crm");
  const partnerMenu = menu.filter((item) => item.group === "partner");
  const isPartnerMode = role === "CHANNEL_PARTNER";

  const initials = (profile?.name ?? role ?? "U")
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  async function handleLogout() {
    try {
      if (refreshToken) {
        await api.post("/auth/logout", { refresh_token: refreshToken });
      }
    } catch {
      // no-op
    } finally {
      dispatch(clearTokens());
      navigate("/login");
    }
  }

  function handleNavigate() {
    setMenuOpen(false);
  }

  return (
    <div className="min-h-screen crm-grid">
      <aside className={`sidebar fixed inset-y-0 left-0 z-40 flex w-[280px] flex-col p-5 transition-transform duration-300 md:static md:h-screen md:translate-x-0 md:p-6 ${menuOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div>
          <div className="flex items-center justify-between gap-3">
            <div>
              <h1 className="font-display text-2xl text-slate-50">{isPartnerMode ? "RPEX Partner" : "RPEX CRM"}</h1>
              <p className="text-slate-300 text-sm mt-1">{isPartnerMode ? "Partner bookings and payout workspace" : "SEO Inquiry Operations"}</p>
            </div>
            <button className="btn-secondary px-3 py-2 text-xs md:hidden" onClick={() => setMenuOpen(false)}>
              Close
            </button>
          </div>
        </div>

        <nav className="mt-8 flex-1 overflow-y-auto pr-1">
          {crmMenu.length ? (
            <div className="space-y-2">
              <p className="px-3 text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">CRM Workspace</p>
              {crmMenu.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={handleNavigate}
                  className={({ isActive }) =>
                    `block rounded-xl px-3 py-2 text-sm font-semibold transition ${
                      isActive ? "bg-slate-100 text-slate-950" : "text-slate-200 hover:bg-slate-800"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          ) : null}

          {partnerMenu.length ? (
            <div className="mt-6 space-y-2">
              <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-cyan-300">Channel Partner</p>
                <p className="mt-1 text-sm text-slate-200">Dedicated portal for bookings, collections, documents, and payout visibility.</p>
              </div>
              {partnerMenu.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={handleNavigate}
                  className={({ isActive }) =>
                    `block rounded-xl px-3 py-2 text-sm font-semibold transition ${
                      isActive ? "bg-cyan-300 text-slate-950" : "text-cyan-100 hover:bg-slate-800"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          ) : null}
        </nav>

        <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-full bg-slate-100 text-slate-950 font-bold">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-100">{profile?.name ?? "Account"}</p>
              <p className="truncate text-xs text-slate-400">{profile?.email ?? "profile syncing..."}</p>
              <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-cyan-300">{profile?.role ?? role ?? "Unknown role"}</p>
              <p className="mt-1 text-xs text-slate-400">{profile?.role_description ?? "System access profile"}</p>
            </div>
          </div>

          <div className="mt-4 space-y-2">
            <div className="rounded-xl bg-slate-950/80 px-3 py-2 text-xs text-slate-300">
              Status: <span className="font-semibold text-emerald-300">{profile?.is_active ? "Active" : "Inactive"}</span>
            </div>
            <div className="rounded-xl bg-slate-950/80 px-3 py-2 text-xs text-slate-300">
              Permissions: <span className="font-semibold text-cyan-300">{profile?.permissions?.length ?? 0}</span>
            </div>
            <button
              className="btn-secondary w-full px-3 py-2 text-sm"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </div>
      </aside>

      {menuOpen ? <button className="fixed inset-0 z-30 bg-slate-950/50 md:hidden" onClick={() => setMenuOpen(false)} aria-label="Close navigation" /> : null}

      <main className="min-w-0 p-4 md:p-8">
        <div className="mb-4 flex items-center justify-between gap-3 md:hidden">
          <button className="btn-secondary px-4 py-2 text-sm" onClick={() => setMenuOpen(true)}>
            Menu
          </button>
          <div className="text-right">
            <p className="text-sm font-semibold text-slate-100">{profile?.name ?? "Account"}</p>
            <p className="text-xs text-slate-400">{profile?.role ?? role ?? "Unknown role"}</p>
          </div>
        </div>
        <Outlet />
      </main>
    </div>
  );
}
