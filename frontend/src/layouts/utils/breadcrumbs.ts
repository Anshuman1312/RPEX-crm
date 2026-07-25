import { BreadcrumbItem, NavigationItem } from "@/layouts/types";

export function buildBreadcrumbs(pathname: string, navItems: NavigationItem[]): BreadcrumbItem[] {
  const cleaned = pathname.split("?")[0];
  const segments = cleaned.split("/").filter(Boolean);

  if (segments.length === 0) {
    return [{ label: "Home", path: "/" }];
  }

  const breadcrumbs: BreadcrumbItem[] = [{ label: "Home", path: "/" }];
  let currentPath = "";

  segments.forEach(segment => {
    currentPath = `${currentPath}/${segment}`;
    const navMatch = navItems.find(item => item.path === currentPath);

    breadcrumbs.push({
      label: navMatch?.label ?? startCase(segment),
      path: currentPath
    });
  });

  return breadcrumbs;
}

function startCase(input: string): string {
  return input
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, char => char.toUpperCase());
}
