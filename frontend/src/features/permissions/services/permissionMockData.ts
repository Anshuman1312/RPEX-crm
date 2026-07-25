import {
  PermissionAction,
  PermissionListResponse,
  PermissionModule,
  PermissionRecord,
  PermissionStats
} from "@/features/permissions/types/permission";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

const coreModules: PermissionModule[] = [
  "Leads",
  "Customers",
  "Bookings",
  "Payments",
  "Reports"
];
const actions: PermissionAction[] = ["view", "create", "edit", "delete"];

let idCounter = 1;

function makePermission(
  module: PermissionModule,
  action: PermissionAction,
  assignedRoles: number,
  status: "Active" | "Inactive" = "Active"
): PermissionRecord {
  const key = `${module.toLowerCase()}:${action}`;
  return {
    id: `PERM-${String(idCounter++).padStart(4, "0")}`,
    key,
    module,
    action,
    status,
    description: `Allows ${action} operations on the ${module} module.`,
    assignedRoles,
    createdAt: formatDate(-600)
  };
}

export const initialPermissionRecords: PermissionRecord[] = [
  ...coreModules.flatMap(module =>
    actions.map((action, i) => makePermission(module, action, i === 0 ? 3 : 1))
  ),
  makePermission("Employees", "view", 2),
  makePermission("Employees", "create", 1),
  makePermission("Roles", "view", 1),
  makePermission("Settings", "view", 2, "Inactive")
];

export function buildPermissionStats(records: PermissionRecord[]): PermissionStats {
  return {
    total: records.length,
    active: records.filter(r => r.status === "Active").length,
    inactive: records.filter(r => r.status === "Inactive").length,
    modules: new Set(records.map(r => r.module)).size
  };
}

export function buildPermissionListResponse(
  records: PermissionRecord[]
): PermissionListResponse {
  return { items: records, total: records.length, stats: buildPermissionStats(records) };
}
