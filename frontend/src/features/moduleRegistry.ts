export interface FeatureModuleDefinition {
  key: string;
  label: string;
  route?: string;
  isScaffoldOnly: boolean;
}

export const featureModuleRegistry: FeatureModuleDefinition[] = [
  { key: "auth", label: "Authentication", route: "/auth/login", isScaffoldOnly: false },
  { key: "dashboard", label: "Dashboard", route: "/dashboard", isScaffoldOnly: false },
  { key: "leads", label: "Lead Management", route: "/leads", isScaffoldOnly: false },
  { key: "campaigns", label: "Campaign Management", route: "/campaigns", isScaffoldOnly: false },
  { key: "followups", label: "Follow-up Management", route: "/followups", isScaffoldOnly: false },
  { key: "customers", label: "Customer Management", route: "/customers", isScaffoldOnly: false },
  { key: "projects", label: "Project Management", route: "/projects", isScaffoldOnly: false },
  { key: "inventory", label: "Inventory", route: "/inventory", isScaffoldOnly: false },
  { key: "bookings", label: "Booking", route: "/bookings", isScaffoldOnly: false },
  { key: "payments", label: "Payments", route: "/payments", isScaffoldOnly: false },
  { key: "tasks", label: "Tasks", route: "/tasks", isScaffoldOnly: false },
  { key: "meetings", label: "Meetings", route: "/meetings", isScaffoldOnly: false },
  { key: "calendar", label: "Calendar", isScaffoldOnly: true },
  { key: "notifications", label: "Notifications", route: "/notifications", isScaffoldOnly: false },
  { key: "reports", label: "Reports", route: "/reports", isScaffoldOnly: false },
  { key: "employees", label: "Employees", isScaffoldOnly: true },
  { key: "organization", label: "Organization", isScaffoldOnly: true },
  { key: "roles", label: "Roles", isScaffoldOnly: true },
  { key: "permissions", label: "Permissions", isScaffoldOnly: true },
  { key: "settings", label: "Settings", route: "/settings", isScaffoldOnly: false },
  { key: "profile", label: "Profile", isScaffoldOnly: true },
  { key: "activity-timeline", label: "Activity Timeline", isScaffoldOnly: true },
  { key: "workflow", label: "Workflow Management", isScaffoldOnly: true }
];
