import { SearchInput } from "@/components";
import { roleScopeOptions, roleStatusOptions } from "@/features/roles/constants/roleOptions";
import { RoleScope, RoleStatus } from "@/features/roles/types/role";

interface Props {
  search: string;
  scope: RoleScope | "All";
  status: RoleStatus | "All";
  onSearchChange: (v: string) => void;
  onScopeChange: (v: RoleScope | "All") => void;
  onStatusChange: (v: RoleStatus | "All") => void;
}

export function RoleFiltersBar({
  search, scope, status, onSearchChange, onScopeChange, onStatusChange
}: Props) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, name, description"
        value={search}
      />
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onScopeChange(e.target.value as RoleScope | "All")}
        value={scope}
      >
        {roleScopeOptions.map(o => (
          <option key={o} value={o}>Scope: {o}</option>
        ))}
      </select>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onStatusChange(e.target.value as RoleStatus | "All")}
        value={status}
      >
        {roleStatusOptions.map(o => (
          <option key={o} value={o}>Status: {o}</option>
        ))}
      </select>
    </section>
  );
}
