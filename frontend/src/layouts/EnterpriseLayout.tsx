import { useEffect, useMemo, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "@/hooks/redux";
import { usePermissions } from "@/hooks/usePermissions";
import { appPaths } from "@/routes/config/paths";
import { tokenStorage } from "@/core/auth/tokenStorage";
import { clearCredentials } from "@/features/auth/store/authSlice";
import { AppFooter } from "@/layouts/components/AppFooter";
import { AppBreadcrumbs } from "@/layouts/components/AppBreadcrumbs";
import { NotificationPanel } from "@/layouts/components/NotificationPanel";
import { ProfileMenu } from "@/layouts/components/ProfileMenu";
import { SidebarNav } from "@/layouts/components/SidebarNav";
import { TopBar } from "@/layouts/components/TopBar";
import { organizations, primaryNavigation, quickSearchScopes } from "@/layouts/config/shell.config";
import { buildBreadcrumbs } from "@/layouts/utils/breadcrumbs";
import { getNextThemeMode } from "@/core/theme/theme.constants";
import {
  setActiveOrganizationId,
  setMobileSidebarOpen,
  setSidebarCollapsed,
  setThemeMode
} from "@/store/uiSlice";

export function EnterpriseLayout() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { hasPermission } = usePermissions();
  const { sidebarCollapsed, mobileSidebarOpen, themeMode, resolvedTheme, activeOrganizationId } = useAppSelector(
    state => state.ui
  );
  const session = useAppSelector(state => state.auth.session);
  const unreadNotifications = 3;

  const handleSignOut = () => {
    tokenStorage.clearAuth();
    dispatch(clearCredentials());
    navigate(appPaths.login, { replace: true });
  };

  useEffect(() => {
    if (!activeOrganizationId) {
      dispatch(setActiveOrganizationId(organizations[0]?.id ?? null));
    }
  }, [activeOrganizationId, dispatch]);

  const allowedNavItems = useMemo(
    () => primaryNavigation.filter(item => hasPermission(item.permission)),
    [hasPermission]
  );

  const breadcrumbs = useMemo(
    () => buildBreadcrumbs(location.pathname, allowedNavItems),
    [location.pathname, allowedNavItems]
  );

  return (
    <div className="min-h-screen bg-background">
      <div className="grid min-h-screen lg:grid-cols-[auto_1fr]">
        <SidebarNav
          activeOrganizationId={activeOrganizationId}
          collapsed={sidebarCollapsed}
          items={allowedNavItems}
          onOrganizationChange={organizationId => dispatch(setActiveOrganizationId(organizationId))}
          onToggleCollapse={() => dispatch(setSidebarCollapsed(!sidebarCollapsed))}
          organizations={organizations}
        />

        {mobileSidebarOpen && (
          <div className="fixed inset-0 z-40 bg-black/35 lg:hidden" onClick={() => dispatch(setMobileSidebarOpen(false))} />
        )}

        <div className={`fixed left-0 top-0 z-50 h-full w-72 lg:hidden ${mobileSidebarOpen ? "block" : "hidden"}`}>
          <SidebarNav
            activeOrganizationId={activeOrganizationId}
            collapsed={false}
            items={allowedNavItems}
            mobile
            onOrganizationChange={organizationId => dispatch(setActiveOrganizationId(organizationId))}
            onToggleCollapse={() => dispatch(setMobileSidebarOpen(false))}
            organizations={organizations}
          />
        </div>

        <div className="flex min-h-screen flex-col min-w-0">
          <TopBar
            themeMode={themeMode}
            resolvedTheme={resolvedTheme}
            onOpenMobileNav={() => dispatch(setMobileSidebarOpen(true))}
            onCycleThemeMode={() => dispatch(setThemeMode(getNextThemeMode(themeMode)))}
            searchScopes={quickSearchScopes}
            unreadNotifications={unreadNotifications}
            userEmail={session?.email ?? "enterprise.user@rpex.com"}
            userName={session?.name ?? "Enterprise User"}
            onSignOut={handleSignOut}
          />

          <main className="flex-1 p-4 lg:p-6 min-w-0">
            <div className="mb-4">
              <AppBreadcrumbs items={breadcrumbs} />
            </div>

            <Outlet />
          </main>

          <AppFooter />
        </div>
      </div>
    </div>
  );
}
