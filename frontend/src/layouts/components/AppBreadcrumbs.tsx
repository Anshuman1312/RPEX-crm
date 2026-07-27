import { Fragment } from "react";
import { Link } from "react-router-dom";
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator
} from "@/components";
import { BreadcrumbItem as BreadcrumbItemType } from "@/layouts/types";

interface AppBreadcrumbsProps {
  items: BreadcrumbItemType[];
}

export function AppBreadcrumbs({ items }: AppBreadcrumbsProps) {
  return (
    <Breadcrumb className="overflow-x-auto text-xs">
      <BreadcrumbList className="flex-nowrap gap-1 sm:gap-1.5 text-xs">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <Fragment key={item.path}>
              {index > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {isLast ? (
                  <BreadcrumbPage className="font-medium text-foreground text-xs">{item.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink asChild className="hover:text-foreground text-xs">
                    <Link to={item.path}>{item.label}</Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
