import { Navigate, Outlet, useLocation } from "react-router-dom";
import { PermissionKey } from "@/config/permissions";
import { usePermissions } from "@/hooks/usePermissions";
import { useAppSelector } from "@/hooks/redux";
import { appPaths } from "@/routes/config/paths";
import { Role } from "@/types/auth";

interface ProtectedRouteProps {
  requiredPermission?: PermissionKey;
  allowedRoles?: Role[];
}

export function ProtectedRoute({ requiredPermission, allowedRoles }: ProtectedRouteProps) {
  const location = useLocation();
  const { accessToken, session, status } = useAppSelector(state => state.auth);
  const { hasPermission } = usePermissions();

  if (status === "unknown") {
    return null;
  }

  if (!accessToken) {
    return <Navigate to={appPaths.login} state={{ from: location }} replace />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to={appPaths.forbidden} replace />;
  }

  if (allowedRoles && session && !allowedRoles.includes(session.role)) {
    return <Navigate to={appPaths.forbidden} replace />;
  }

  return <Outlet />;
}
