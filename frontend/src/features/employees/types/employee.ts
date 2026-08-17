export type EmployeeDepartment = "Sales" | "Operations" | "Finance" | "Marketing" | "HR";
export type EmployeeStatus = "Active" | "On Leave" | "Inactive";
export type EmployeeBand = "Associate" | "Senior" | "Lead" | "Manager";

export interface EmployeeRecord {
  id: string;
  fullName: string;
  email: string;
  department: string;
  band: string;
  manager: string;
  status: EmployeeStatus;
  joiningDate: string;
  updatedAt: string;
  // Database fields
  roleName?: string;
  roleId?: string;
  departmentId?: string;
  designationId?: string;
}

export interface EmployeeFilters {
  search?: string;
  department?: string;
  status?: string;
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
  password?: string;
  phone?: string;
  departmentId?: string;
  designationId?: string;
  roleId?: string;
  employeeCode?: string;
}
