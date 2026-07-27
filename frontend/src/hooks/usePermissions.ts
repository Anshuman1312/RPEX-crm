import { PermissionKey } from "@/config/permissions";
import { useAppSelector } from "@/hooks/redux";

export function usePermissions() {
  const authStatus = useAppSelector(state => state.auth.status);
  const permissions = useAppSelector(state => state.auth.session?.permissions ?? []);

  const hasPermission = (permission: PermissionKey) => {
    if (permissions.length === 0 && authStatus === "authenticated") {
      return true;
    }

    return permissions.includes(permission);
  };

  return {
    permissions,
    hasPermission
  };
}
