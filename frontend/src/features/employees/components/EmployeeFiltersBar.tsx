import { SearchInput } from "@/components";
import {
  employeeDepartmentOptions,
  employeeStatusOptions
} from "@/features/employees/constants/employeeOptions";
import {
  EmployeeDepartment,
  EmployeeStatus
} from "@/features/employees/types/employee";

interface EmployeeFiltersBarProps {
  search: string;
  department: EmployeeDepartment | "All";
  status: EmployeeStatus | "All";
  onSearchChange: (value: string) => void;
  onDepartmentChange: (value: EmployeeDepartment | "All") => void;
  onStatusChange: (value: EmployeeStatus | "All") => void;
}

export function EmployeeFiltersBar({
  search,
  department,
  status,
  onSearchChange,
  onDepartmentChange,
  onStatusChange
}: EmployeeFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, name, email, manager, department"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onDepartmentChange(event.target.value as EmployeeDepartment | "All")}
        value={department}
      >
        {employeeDepartmentOptions.map(option => (
          <option key={option} value={option}>
            Department: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as EmployeeStatus | "All")}
        value={status}
      >
        {employeeStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
