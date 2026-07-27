import { SearchInput } from "@/components";
import {
  activityActionOptions,
  activityModuleOptions
} from "@/features/activity-timeline/constants/activityOptions";
import {
  ActivityAction,
  ActivityModule
} from "@/features/activity-timeline/types/activity";

interface Props {
  search: string;
  module: ActivityModule | "All";
  action: ActivityAction | "All";
  onSearchChange: (v: string) => void;
  onModuleChange: (v: ActivityModule | "All") => void;
  onActionChange: (v: ActivityAction | "All") => void;
}

export function ActivityFiltersBar({
  search, module, action, onSearchChange, onModuleChange, onActionChange
}: Props) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, actor, module, subject, detail"
        value={search}
      />
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onModuleChange(e.target.value as ActivityModule | "All")}
        value={module}
      >
        {activityModuleOptions.map(o => (
          <option key={o} value={o}>Module: {o}</option>
        ))}
      </select>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onActionChange(e.target.value as ActivityAction | "All")}
        value={action}
      >
        {activityActionOptions.map(o => (
          <option key={o} value={o}>Action: {o}</option>
        ))}
      </select>
    </section>
  );
}
