import { lazy, LazyExoticComponent } from "react";
import type { ReactElement } from "react";
import { PermissionKey } from "@/config/permissions";
import { appPaths } from "@/routes/config/paths";

type LazyPage = LazyExoticComponent<() => ReactElement>;

export interface ModuleRouteDefinition {
  key: string;
  path: string;
  permission: PermissionKey;
  breadcrumb: string;
  component: LazyPage;
}

function lazyNamed<TModule extends Record<string, unknown>, TKey extends keyof TModule>(
  importer: () => Promise<TModule>,
  key: TKey
): LazyExoticComponent<() => ReactElement> {
  return lazy(async () => {
    const module = await importer();
    return { default: module[key] as () => ReactElement };
  });
}

const DashboardPage = lazyNamed(() => import("@/features/dashboard/pages/DashboardPage"), "DashboardPage");
const LeadsPage = lazyNamed(() => import("@/features/leads/pages/LeadsPage"), "LeadsPage");
const CampaignsPage = lazyNamed(() => import("@/features/campaigns/pages/CampaignsPage"), "CampaignsPage");
const FollowUpsPage = lazyNamed(() => import("@/features/followups/pages/FollowUpsPage"), "FollowUpsPage");
const CustomersPage = lazyNamed(() => import("@/features/customers/pages/CustomersPage"), "CustomersPage");
const ProjectsPage = lazyNamed(() => import("@/features/projects/pages/ProjectsPage"), "ProjectsPage");
const InventoryPage = lazyNamed(() => import("@/features/inventory/pages/InventoryPage"), "InventoryPage");
const BookingsPage = lazyNamed(() => import("@/features/bookings/pages/BookingsPage"), "BookingsPage");
const PaymentsPage = lazyNamed(() => import("@/features/payments/pages/PaymentsPage"), "PaymentsPage");
const TasksPage = lazyNamed(() => import("@/features/tasks/pages/TasksPage"), "TasksPage");
const MeetingsPage = lazyNamed(() => import("@/features/meetings/pages/MeetingsPage"), "MeetingsPage");
const CalendarPage = lazyNamed(() => import("@/features/calendar/pages/CalendarPage"), "CalendarPage");
const NotificationsPage = lazyNamed(() => import("@/features/notifications/pages/NotificationsPage"), "NotificationsPage");
const ReportsPage = lazyNamed(() => import("@/features/reports/pages/ReportsPage"), "ReportsPage");
const EmployeesPage = lazyNamed(() => import("@/features/employees/pages/EmployeesPage"), "EmployeesPage");
const OrganizationPage = lazyNamed(() => import("@/features/organization/pages/OrganizationPage"), "OrganizationPage");
const RolesPage = lazyNamed(() => import("@/features/roles/pages/RolesPage"), "RolesPage");
const PermissionsPage = lazyNamed(() => import("@/features/permissions/pages/PermissionsPage"), "PermissionsPage");
const ProfilePage = lazyNamed(() => import("@/features/profile/pages/ProfilePage"), "ProfilePage");
const ActivityTimelinePage = lazyNamed(() => import("@/features/activity-timeline/pages/ActivityTimelinePage"), "ActivityTimelinePage");
const WorkflowPage = lazyNamed(() => import("@/features/workflow/pages/WorkflowPage"), "WorkflowPage");
const SettingsPage = lazyNamed(() => import("@/features/settings/pages/SettingsPage"), "SettingsPage");

export const moduleRouteCatalog: ModuleRouteDefinition[] = [
  {
    key: "dashboard",
    path: appPaths.dashboard,
    permission: "dashboard:view",
    breadcrumb: "Dashboard",
    component: DashboardPage
  },
  {
    key: "leads",
    path: appPaths.leads,
    permission: "leads:view",
    breadcrumb: "Leads",
    component: LeadsPage
  },
  {
    key: "campaigns",
    path: appPaths.campaigns,
    permission: "campaigns:view",
    breadcrumb: "Campaigns",
    component: CampaignsPage
  },
  {
    key: "followups",
    path: appPaths.followups,
    permission: "followups:view",
    breadcrumb: "Follow-ups",
    component: FollowUpsPage
  },
  {
    key: "customers",
    path: appPaths.customers,
    permission: "customers:view",
    breadcrumb: "Customers",
    component: CustomersPage
  },
  {
    key: "projects",
    path: appPaths.projects,
    permission: "projects:view",
    breadcrumb: "Projects",
    component: ProjectsPage
  },
  {
    key: "inventory",
    path: appPaths.inventory,
    permission: "inventory:view",
    breadcrumb: "Inventory",
    component: InventoryPage
  },
  {
    key: "bookings",
    path: appPaths.bookings,
    permission: "bookings:view",
    breadcrumb: "Bookings",
    component: BookingsPage
  },
  {
    key: "payments",
    path: appPaths.payments,
    permission: "payments:view",
    breadcrumb: "Payments",
    component: PaymentsPage
  },
  {
    key: "tasks",
    path: appPaths.tasks,
    permission: "tasks:view",
    breadcrumb: "Tasks",
    component: TasksPage
  },
  {
    key: "meetings",
    path: appPaths.meetings,
    permission: "meetings:view",
    breadcrumb: "Meetings",
    component: MeetingsPage
  },
  {
    key: "calendar",
    path: appPaths.calendar,
    permission: "calendar:view",
    breadcrumb: "Calendar",
    component: CalendarPage
  },
  {
    key: "notifications",
    path: appPaths.notifications,
    permission: "notifications:view",
    breadcrumb: "Notifications",
    component: NotificationsPage
  },
  {
    key: "reports",
    path: appPaths.reports,
    permission: "reports:view",
    breadcrumb: "Reports",
    component: ReportsPage
  },
  {
    key: "employees",
    path: appPaths.employees,
    permission: "employees:view",
    breadcrumb: "Employees",
    component: EmployeesPage
  },
  {
    key: "organization",
    path: appPaths.organization,
    permission: "organization:view",
    breadcrumb: "Organization",
    component: OrganizationPage
  },
  {
    key: "roles",
    path: appPaths.roles,
    permission: "roles:view",
    breadcrumb: "Roles",
    component: RolesPage
  },
  {
    key: "permissions",
    path: appPaths.permissions,
    permission: "permissions:view",
    breadcrumb: "Permissions",
    component: PermissionsPage
  },
  {
    key: "profile",
    path: appPaths.profile,
    permission: "profile:view",
    breadcrumb: "My Profile",
    component: ProfilePage
  },
  {
    key: "activity-timeline",
    path: appPaths.activityTimeline,
    permission: "activity-timeline:view",
    breadcrumb: "Activity Timeline",
    component: ActivityTimelinePage
  },
  {
    key: "workflow",
    path: appPaths.workflow,
    permission: "workflow:view",
    breadcrumb: "Workflow",
    component: WorkflowPage
  },
  {
    key: "settings",
    path: appPaths.settings,
    permission: "settings:view",
    breadcrumb: "Settings",
    component: SettingsPage
  }
];
