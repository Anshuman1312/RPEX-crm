import { ChevronLeft, ChevronRight } from "lucide-react";
import { NavLink } from "react-router-dom";
import { Button, ScrollArea } from "@/components";
import { cn } from "@/utils/cn";
import { NavigationItem, OrganizationOption } from "@/layouts/types";

interface SidebarNavProps {
  items: NavigationItem[];
  organizations: OrganizationOption[];
  activeOrganizationId: string | null;
  collapsed: boolean;
  mobile?: boolean;
  onToggleCollapse: () => void;
  onOrganizationChange: (organizationId: string) => void;
}

export function SidebarNav({
  items,
  organizations,
  activeOrganizationId,
  collapsed,
  mobile = false,
  onToggleCollapse,
  onOrganizationChange
}: SidebarNavProps) {
  return (
    <aside
      className={cn(
        "border-r bg-card transition-all duration-200 flex flex-col h-screen sticky top-0 z-20 overflow-hidden",
        mobile ? "h-full w-full" : "hidden lg:block",
        collapsed ? "w-20" : "w-72"
      )}
    >
      <div className="flex h-16 items-center justify-between border-b px-4 shrink-0">
        <div className="flex items-center gap-2">
          <img src="/logo.png" alt="RPEX CRM Logo" className="h-6 w-6 object-contain" />
          {!collapsed && <span className="text-sm font-semibold">RPEX CRM</span>}
        </div>
        <Button variant="ghost" size="sm" onClick={onToggleCollapse}>
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {!collapsed && (
        <div className="border-b p-3 shrink-0">
          <label className="mb-1 block text-xs font-medium text-muted-foreground" htmlFor="org-switcher">
            Organization
          </label>
          <select
            className="h-9 w-full rounded-md border bg-background px-2 text-sm"
            id="org-switcher"
            onChange={event => onOrganizationChange(event.target.value)}
            value={activeOrganizationId ?? organizations[0]?.id ?? ""}
          >
            {organizations.map(org => (
              <option key={org.id} value={org.id}>
                {org.label}
              </option>
            ))}
          </select>
        </div>
      )}

      <ScrollArea className="flex-1">
        <nav className="p-3 pb-12">
          {items.map(item => {
            const Icon = item.icon;
            return (
              <NavLink
                className={({ isActive }) =>
                  cn(
                    "mb-1 flex items-center gap-2 rounded-md px-3 py-2 text-sm transition",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )
                }
                key={item.id}
                to={item.path}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>
      </ScrollArea>
    </aside>
  );
}
