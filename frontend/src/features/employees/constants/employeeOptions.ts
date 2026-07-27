import {
  EmployeeBand,
  EmployeeDepartment,
  EmployeeStatus
} from "@/features/employees/types/employee";

export const employeeDepartmentOptions: Array<EmployeeDepartment | "All"> = [
  "All",
  "Sales",
  "Operations",
  "Finance",
  "Marketing",
  "HR"
];

export const employeeStatusOptions: Array<EmployeeStatus | "All"> = [
  "All",
  "Active",
  "On Leave",
  "Inactive"
];

export const employeeBandOptions: EmployeeBand[] = [
  "Associate",
  "Senior",
  "Lead",
  "Manager"
];
