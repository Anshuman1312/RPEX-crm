import { RoleScope, RoleStatus } from "@/features/roles/types/role";

export const roleScopeOptions: Array<RoleScope | "All"> = [
  "All",
  "System",
  "Organization",
  "Module"
];

export const roleStatusOptions: Array<RoleStatus | "All"> = ["All", "Active", "Inactive"];
