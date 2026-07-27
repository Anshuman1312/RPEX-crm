import {
  Activity,
  BarChart3,
  Bell,
  Boxes,
  Building2,
  CalendarDays,
  BriefcaseBusiness,
  CalendarClock,
  ClipboardList,
  CreditCard,
  FolderKanban,
  Gauge,
  GitBranch,
  KeyRound,
  Megaphone,
  PhoneCall,
  ShieldCheck,
  Settings,
  UserCircle,
  Users,
  UserRoundSearch
} from "lucide-react";
import { NavigationItem, OrganizationOption, ShellSearchScope } from "@/layouts/types";
import { appPaths } from "@/routes/config/paths";

export const organizations: OrganizationOption[] = [
  { id: "org-rpex", label: "RPEX Group" },
  { id: "org-apex", label: "Apex Ventures" },
  { id: "org-orbit", label: "Orbit Realty" }
];

export const quickSearchScopes: ShellSearchScope[] = [
  { id: "all", label: "All Modules" },
  { id: "leads", label: "Leads" },
  { id: "campaigns", label: "Campaigns" },
  { id: "followups", label: "Follow-ups" },
  { id: "customers", label: "Customers" },
  { id: "projects", label: "Projects" },
  { id: "inventory", label: "Inventory" },
  { id: "calendar", label: "Calendar" },
  { id: "employees", label: "Employees" }
];

export const primaryNavigation: NavigationItem[] = [
  { id: "dashboard", label: "Dashboard", path: appPaths.dashboard, permission: "dashboard:view", icon: Gauge, module: "analytics" },
  { id: "leads", label: "Leads", path: appPaths.leads, permission: "leads:view", icon: UserRoundSearch, module: "sales" },
  { id: "campaigns", label: "Campaigns", path: appPaths.campaigns, permission: "campaigns:view", icon: Megaphone, module: "sales" },
  { id: "followups", label: "Follow-ups", path: appPaths.followups, permission: "followups:view", icon: PhoneCall, module: "sales" },
  { id: "customers", label: "Customers", path: appPaths.customers, permission: "customers:view", icon: Users, module: "sales" },
  { id: "projects", label: "Projects", path: appPaths.projects, permission: "projects:view", icon: FolderKanban, module: "delivery" },
  { id: "inventory", label: "Inventory", path: appPaths.inventory, permission: "inventory:view", icon: Boxes, module: "operations" },
  { id: "bookings", label: "Bookings", path: appPaths.bookings, permission: "bookings:view", icon: BriefcaseBusiness, module: "operations" },
  { id: "payments", label: "Payments", path: appPaths.payments, permission: "payments:view", icon: CreditCard, module: "finance" },
  { id: "tasks", label: "Tasks", path: appPaths.tasks, permission: "tasks:view", icon: ClipboardList, module: "execution" },
  { id: "meetings", label: "Meetings", path: appPaths.meetings, permission: "meetings:view", icon: CalendarClock, module: "execution" },
  { id: "calendar", label: "Calendar", path: appPaths.calendar, permission: "calendar:view", icon: CalendarDays, module: "execution" },
  { id: "notifications", label: "Notifications", path: appPaths.notifications, permission: "notifications:view", icon: Bell, module: "system" },
  { id: "reports", label: "Reports", path: appPaths.reports, permission: "reports:view", icon: BarChart3, module: "analytics" },
  { id: "employees", label: "Employees", path: appPaths.employees, permission: "employees:view", icon: Users, module: "people" },
  { id: "organization", label: "Organization", path: appPaths.organization, permission: "organization:view", icon: Building2, module: "people" },
  { id: "roles", label: "Roles", path: appPaths.roles, permission: "roles:view", icon: ShieldCheck, module: "admin" },
  { id: "permissions", label: "Permissions", path: appPaths.permissions, permission: "permissions:view", icon: KeyRound, module: "admin" },
  { id: "profile", label: "My Profile", path: appPaths.profile, permission: "profile:view", icon: UserCircle, module: "account" },
  { id: "activity-timeline", label: "Activity Timeline", path: appPaths.activityTimeline, permission: "activity-timeline:view", icon: Activity, module: "admin" },
  { id: "workflow", label: "Workflow", path: appPaths.workflow, permission: "workflow:view", icon: GitBranch, module: "admin" },
  { id: "settings", label: "Settings", path: appPaths.settings, permission: "settings:view", icon: Settings, module: "system" }
];
