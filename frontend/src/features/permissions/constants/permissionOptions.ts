import {
  PermissionAction,
  PermissionModule,
  PermissionStatus
} from "@/features/permissions/types/permission";

export const permissionModuleOptions: Array<PermissionModule | "All"> = [
  "All",
  "Leads",
  "Customers",
  "Projects",
  "Inventory",
  "Bookings",
  "Payments",
  "Tasks",
  "Meetings",
  "Calendar",
  "Reports",
  "Employees",
  "Organization",
  "Roles",
  "Settings"
];

export const permissionActionOptions: Array<PermissionAction | "All"> = [
  "All",
  "view",
  "create",
  "edit",
  "delete"
];

export const permissionStatusOptions: Array<PermissionStatus | "All"> = [
  "All",
  "Active",
  "Inactive"
];
