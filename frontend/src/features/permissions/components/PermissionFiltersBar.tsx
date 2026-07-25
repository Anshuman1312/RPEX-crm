import { SearchInput } from "@/components";
import {
  permissionActionOptions,
  permissionModuleOptions,
  permissionStatusOptions
} from "@/features/permissions/constants/permissionOptions";
import {
  PermissionAction,
  PermissionModule,
  PermissionStatus
} from "@/features/permissions/types/permission";

interface Props {
  search: string;
  module: PermissionModule | "All";
  action: PermissionAction | "All";
  status: PermissionStatus | "All";
  onSearchChange: (v: string) => void;
  onModuleChange: (v: PermissionModule | "All") => void;
  onActionChange: (v: PermissionAction | "All") => void;
  onStatusChange: (v: PermissionStatus | "All") => void;
}

export function PermissionFiltersBar({
  search, module, action, status,
  onSearchChange, onModuleChange, onActionChange, onStatusChange
}: Props) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, key, module, description"
        value={search}
      />
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onModuleChange(e.target.value as PermissionModule | "All")}
        value={module}
      >
        {permissionModuleOptions.map(o => (
          <option key={o} value={o}>Module: {o}</option>
        ))}
      </select>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onActionChange(e.target.value as PermissionAction | "All")}
        value={action}
      >
        {permissionActionOptions.map(o => (
          <option key={o} value={o}>Action: {o}</option>
        ))}
      </select>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onStatusChange(e.target.value as PermissionStatus | "All")}
        value={status}
      >
        {permissionStatusOptions.map(o => (
          <option key={o} value={o}>Status: {o}</option>
        ))}
      </select>
    </section>
  );
}
