import { SearchInput } from "@/components";
import {
  taskPriorityOptions,
  taskStatusOptions
} from "@/features/tasks/constants/taskOptions";
import {
  TaskPriority,
  TaskStatus
} from "@/features/tasks/types/task";

interface TaskFiltersBarProps {
  search: string;
  priority: TaskPriority | "All";
  status: TaskStatus | "All";
  onSearchChange: (value: string) => void;
  onPriorityChange: (value: TaskPriority | "All") => void;
  onStatusChange: (value: TaskStatus | "All") => void;
}

export function TaskFiltersBar({
  search,
  priority,
  status,
  onSearchChange,
  onPriorityChange,
  onStatusChange
}: TaskFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by task id, title, module, assignee"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onPriorityChange(event.target.value as TaskPriority | "All")}
        value={priority}
      >
        {taskPriorityOptions.map(option => (
          <option key={option} value={option}>
            Priority: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as TaskStatus | "All")}
        value={status}
      >
        {taskStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
