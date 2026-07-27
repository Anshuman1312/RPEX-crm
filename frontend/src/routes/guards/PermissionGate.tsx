import { PropsWithChildren } from "react";
import { PermissionKey } from "@/config/permissions";
import { usePermissions } from "@/hooks/usePermissions";

interface PermissionGateProps extends PropsWithChildren {
  permission: PermissionKey;
  fallback?: React.ReactNode;
}

export function PermissionGate({ permission, fallback = null, children }: PermissionGateProps) {
  const { hasPermission } = usePermissions();

  if (!hasPermission(permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
