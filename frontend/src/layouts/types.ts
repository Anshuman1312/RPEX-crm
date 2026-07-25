import { LucideIcon } from "lucide-react";
import { PermissionKey } from "@/config/permissions";

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  permission: PermissionKey;
  icon: LucideIcon;
  module: string;
}

export interface OrganizationOption {
  id: string;
  label: string;
}

export interface ShellSearchScope {
  id: string;
  label: string;
}

export interface BreadcrumbItem {
  label: string;
  path: string;
}
