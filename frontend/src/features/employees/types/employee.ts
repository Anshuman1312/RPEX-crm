export type EmployeeDepartment = "Sales" | "Operations" | "Finance" | "Marketing" | "HR";
export type EmployeeStatus = "Active" | "On Leave" | "Inactive";
export type EmployeeBand = "Associate" | "Senior" | "Lead" | "Manager";

export interface EmployeeRecord {
  id: string;
  fullName: string;
  email: string;
  department: EmployeeDepartment;
  band: EmployeeBand;
  manager: string;
  status: EmployeeStatus;
  joiningDate: string;
  updatedAt: string;
}

export interface EmployeeFilters {
  search?: string;
  department?: EmployeeDepartment | "All";
  status?: EmployeeStatus | "All";
}

export interface EmployeeStats {
  total: number;
  active: number;
  onLeave: number;
  inactive: number;
}

export interface EmployeeListResponse {
  items: EmployeeRecord[];
  total: number;
  stats: EmployeeStats;
}

export interface CreateEmployeeInput {
  fullName: string;
  email: string;
  department: EmployeeDepartment;
  band: EmployeeBand;
  manager: string;
  joiningDate: string;
}
