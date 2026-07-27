import { SearchInput } from "@/components";
import { workflowStatusOptions, workflowTriggerOptions } from "@/features/workflow/constants/workflowOptions";
import { WorkflowStatus, WorkflowTrigger } from "@/features/workflow/types/workflow";

interface Props {
  search: string;
  trigger: WorkflowTrigger | "All";
  status: WorkflowStatus | "All";
  onSearchChange: (v: string) => void;
  onTriggerChange: (v: WorkflowTrigger | "All") => void;
  onStatusChange: (v: WorkflowStatus | "All") => void;
}

export function WorkflowFiltersBar({
  search, trigger, status, onSearchChange, onTriggerChange, onStatusChange
}: Props) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, name, trigger, action, module"
        value={search}
      />
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onTriggerChange(e.target.value as WorkflowTrigger | "All")}
        value={trigger}
      >
        {workflowTriggerOptions.map(o => (
          <option key={o} value={o}>Trigger: {o}</option>
        ))}
      </select>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onStatusChange(e.target.value as WorkflowStatus | "All")}
        value={status}
      >
        {workflowStatusOptions.map(o => (
          <option key={o} value={o}>Status: {o}</option>
        ))}
      </select>
    </section>
  );
}
