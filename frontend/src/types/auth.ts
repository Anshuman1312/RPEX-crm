import { PermissionKey } from "@/config/permissions";

export type Role =
  | "SUPER_ADMIN"
  | "ADMIN"
  | "SALES_MANAGER"
  | "SALES_EXECUTIVE"
  | "CRM_EXECUTIVE"
  | "PROJECT_HEAD"
  | "FINANCE"
  | "HR"
  | "ANALYST";

export interface UserSession {
  userId: string;
  name: string;
  email: string;
  role: Role;
  permissions: PermissionKey[];
}
