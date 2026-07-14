import { useMemo } from "react";
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
  roles: Array<"ADMIN" | "SEO_MANAGER" | "SALES" | "ANALYST">;
};

const MENU_ITEMS: MenuItem[] = [
  { label: "Dashboard", path: "/dashboard", roles: ["ADMIN", "SEO_MANAGER", "SALES", "ANALYST"] },
  { label: "Leads", path: "/leads", roles: ["ADMIN", "SEO_MANAGER", "SALES", "ANALYST"] },
  { label: "Campaigns", path: "/campaigns", roles: ["ADMIN", "SEO_MANAGER"] },
  { label: "Keywords", path: "/keywords", roles: ["ADMIN", "SEO_MANAGER", "ANALYST"] },
  { label: "Follow-ups", path: "/followups", roles: ["ADMIN", "SALES"] },
  { label: "Reports", path: "/reports", roles: ["ADMIN", "ANALYST"] }
];

export function AppShell() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { role, refreshToken } = useSelector((state: RootState) => state.auth);
  const { data: profile } = useQuery({ queryKey: ["current-user-profile"], queryFn: fetchCurrentUserProfile });

  const menu = useMemo(
    () => MENU_ITEMS.filter((item) => (role ? item.roles.includes(role) : false)),
    [role]
  );

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

  return (
    <div className="min-h-screen crm-grid">
      <aside className="sidebar flex h-screen flex-col p-5 md:p-6">
        <div>
          <h1 className="font-display text-2xl text-slate-50">RPEX CRM</h1>
          <p className="text-slate-300 text-sm mt-1">SEO Inquiry Operations</p>
        </div>

        <nav className="mt-8 space-y-2 flex-1 overflow-y-auto pr-1">
          {menu.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `block rounded-xl px-3 py-2 text-sm font-semibold transition ${
                  isActive ? "bg-slate-100 text-slate-950" : "text-slate-200 hover:bg-slate-800"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
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
            </div>
          </div>

          <div className="mt-4 space-y-2">
            <div className="rounded-xl bg-slate-950/80 px-3 py-2 text-xs text-slate-300">
              Status: <span className="font-semibold text-emerald-300">{profile?.is_active ? "Active" : "Inactive"}</span>
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

      <main className="p-4 md:p-8">
        <Outlet />
      </main>
    </div>
  );
}
