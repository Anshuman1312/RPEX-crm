export type ActivityModule =
  | "Leads"
  | "Customers"
  | "Bookings"
  | "Payments"
  | "Inventory"
  | "Projects"
  | "Tasks"
  | "Meetings"
  | "Calendar"
  | "Reports"
  | "Employees"
  | "Organization"
  | "Roles"
  | "Settings";

export type ActivityAction =
  | "created"
  | "updated"
  | "deleted"
  | "stage_changed"
  | "status_changed"
  | "assigned"
  | "exported"
  | "login"
  | "logout";

export interface ActivityRecord {
  id: string;
  actor: string;
  module: ActivityModule;
  action: ActivityAction;
  subject: string;
  detail: string;
  occurredAt: string;
}

export interface ActivityFilters {
  search?: string;
  module?: ActivityModule | "All";
  action?: ActivityAction | "All";
}

export interface ActivityStats {
  total: number;
  today: number;
  uniqueActors: number;
  modules: number;
}

export interface ActivityListResponse {
  items: ActivityRecord[];
  total: number;
  stats: ActivityStats;
}
