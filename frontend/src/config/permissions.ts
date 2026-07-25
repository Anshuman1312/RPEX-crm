import { appPaths } from "@/routes/config/paths";

export type PermissionKey =
  | "dashboard:view"
  | "leads:view"
  | "campaigns:view"
  | "followups:view"
  | "customers:view"
  | "projects:view"
  | "inventory:view"
  | "bookings:view"
  | "payments:view"
  | "tasks:view"
  | "meetings:view"
  | "calendar:view"
  | "notifications:view"
  | "reports:view"
  | "employees:view"
  | "organization:view"
  | "roles:view"
  | "permissions:view"
  | "profile:view"
  | "activity-timeline:view"
  | "workflow:view"
  | "settings:view";

export const routePermissionMap: Record<string, PermissionKey> = {
  [appPaths.dashboard]: "dashboard:view",
  [appPaths.leads]: "leads:view",
  [appPaths.campaigns]: "campaigns:view",
  [appPaths.followups]: "followups:view",
  [appPaths.customers]: "customers:view",
  [appPaths.projects]: "projects:view",
  [appPaths.inventory]: "inventory:view",
  [appPaths.bookings]: "bookings:view",
  [appPaths.payments]: "payments:view",
  [appPaths.tasks]: "tasks:view",
  [appPaths.meetings]: "meetings:view",
  [appPaths.calendar]: "calendar:view",
  [appPaths.notifications]: "notifications:view",
  [appPaths.reports]: "reports:view",
  [appPaths.employees]: "employees:view",
  [appPaths.organization]: "organization:view",
  [appPaths.roles]: "roles:view",
  [appPaths.permissions]: "permissions:view",
  [appPaths.profile]: "profile:view",
  [appPaths.activityTimeline]: "activity-timeline:view",
  [appPaths.workflow]: "workflow:view",
  [appPaths.settings]: "settings:view"
};
