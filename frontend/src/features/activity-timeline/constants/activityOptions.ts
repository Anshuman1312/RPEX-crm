import {
  ActivityAction,
  ActivityModule
} from "@/features/activity-timeline/types/activity";

export const activityModuleOptions: Array<ActivityModule | "All"> = [
  "All",
  "Leads",
  "Customers",
  "Bookings",
  "Payments",
  "Inventory",
  "Projects",
  "Tasks",
  "Meetings",
  "Calendar",
  "Reports",
  "Employees",
  "Organization",
  "Roles",
  "Settings"
];

export const activityActionOptions: Array<ActivityAction | "All"> = [
  "All",
  "created",
  "updated",
  "deleted",
  "stage_changed",
  "status_changed",
  "assigned",
  "exported",
  "login",
  "logout"
];
