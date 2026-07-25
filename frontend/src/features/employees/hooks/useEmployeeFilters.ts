import { useMemo, useState } from "react";
import {
  EmployeeDepartment,
  EmployeeFilters,
  EmployeeStatus
} from "@/features/employees/types/employee";

export function useEmployeeFilters() {
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState<EmployeeDepartment | "All">("All");
  const [status, setStatus] = useState<EmployeeStatus | "All">("All");

  const filters = useMemo<EmployeeFilters>(
    () => ({
      search,
      department,
      status
    }),
    [department, search, status]
  );

  return {
    filters,
    search,
    department,
    status,
    setSearch,
    setDepartment,
    setStatus
  };
}
