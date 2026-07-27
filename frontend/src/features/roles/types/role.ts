export type RoleScope = "System" | "Organization" | "Module";
export type RoleStatus = "Active" | "Inactive";

export interface RolePermissionEntry {
  module: string;
  canView: boolean;
  canCreate: boolean;
  canEdit: boolean;
  canDelete: boolean;
}

export interface RoleRecord {
  id: string;
  name: string;
  scope: RoleScope;
  status: RoleStatus;
  description: string;
  assignedUsers: number;
  permissions: RolePermissionEntry[];
  createdAt: string;
  updatedAt: string;
}

export interface RoleFilters {
  search?: string;
  scope?: RoleScope | "All";
  status?: RoleStatus | "All";
}

export interface RoleStats {
  total: number;
  active: number;
  system: number;
  inactive: number;
}

export interface RoleListResponse {
  items: RoleRecord[];
  total: number;
  stats: RoleStats;
}

export interface CreateRoleInput {
  name: string;
  scope: RoleScope;
  description: string;
}
