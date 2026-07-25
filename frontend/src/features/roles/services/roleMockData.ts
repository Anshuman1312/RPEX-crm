import {
  CreateRoleInput,
  RoleListResponse,
  RolePermissionEntry,
  RoleRecord,
  RoleStats
} from "@/features/roles/types/role";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

const coreModules = ["Leads", "Customers", "Bookings", "Payments", "Inventory", "Reports"];

function fullAccess(module: string): RolePermissionEntry {
  return { module, canView: true, canCreate: true, canEdit: true, canDelete: true };
}

function readOnly(module: string): RolePermissionEntry {
  return { module, canView: true, canCreate: false, canEdit: false, canDelete: false };
}

export const initialRoleRecords: RoleRecord[] = [
  {
    id: "ROLE-001",
    name: "Super Admin",
    scope: "System",
    status: "Active",
    description: "Unrestricted access to all modules and configuration.",
    assignedUsers: 2,
    permissions: coreModules.map(fullAccess),
    createdAt: formatDate(-900),
    updatedAt: formatDate(-1)
  },
  {
    id: "ROLE-002",
    name: "Sales Manager",
    scope: "Organization",
    status: "Active",
    description: "Full access to sales pipeline, bookings, and customer lifecycle.",
    assignedUsers: 8,
    permissions: ["Leads", "Customers", "Bookings"].map(fullAccess),
    createdAt: formatDate(-600),
    updatedAt: formatDate(-3)
  },
  {
    id: "ROLE-003",
    name: "Finance Analyst",
    scope: "Module",
    status: "Active",
    description: "Read-only access to payments, invoices, and financial reports.",
    assignedUsers: 4,
    permissions: ["Payments", "Reports"].map(readOnly),
    createdAt: formatDate(-400),
    updatedAt: formatDate(-5)
  },
  {
    id: "ROLE-004",
    name: "Legacy Viewer",
    scope: "Organization",
    status: "Inactive",
    description: "Deprecated viewer role kept for audit purposes.",
    assignedUsers: 0,
    permissions: coreModules.map(readOnly),
    createdAt: formatDate(-1200),
    updatedAt: formatDate(-90)
  }
];

export function buildRoleStats(records: RoleRecord[]): RoleStats {
  return {
    total: records.length,
    active: records.filter(r => r.status === "Active").length,
    system: records.filter(r => r.scope === "System").length,
    inactive: records.filter(r => r.status === "Inactive").length
  };
}

export function buildRoleListResponse(records: RoleRecord[]): RoleListResponse {
  return { items: records, total: records.length, stats: buildRoleStats(records) };
}

export function createRoleRecord(payload: CreateRoleInput, index: number): RoleRecord {
  const today = new Date().toISOString().slice(0, 10);
  return {
    id: `ROLE-${String(index).padStart(3, "0")}`,
    name: payload.name,
    scope: payload.scope,
    status: "Active",
    description: payload.description,
    assignedUsers: 0,
    permissions: [],
    createdAt: today,
    updatedAt: today
  };
}
