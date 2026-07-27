export type PermissionModule =
  | "Leads"
  | "Customers"
  | "Projects"
  | "Inventory"
  | "Bookings"
  | "Payments"
  | "Tasks"
  | "Meetings"
  | "Calendar"
  | "Reports"
  | "Employees"
  | "Organization"
  | "Roles"
  | "Settings";

export type PermissionAction = "view" | "create" | "edit" | "delete";
export type PermissionStatus = "Active" | "Inactive";

export interface PermissionRecord {
  id: string;
  key: string;
  module: PermissionModule;
  action: PermissionAction;
  status: PermissionStatus;
  description: string;
  assignedRoles: number;
  createdAt: string;
}

export interface PermissionFilters {
  search?: string;
  module?: PermissionModule | "All";
  action?: PermissionAction | "All";
  status?: PermissionStatus | "All";
}

export interface PermissionStats {
  total: number;
  active: number;
  inactive: number;
  modules: number;
}

export interface PermissionListResponse {
  items: PermissionRecord[];
  total: number;
  stats: PermissionStats;
}
