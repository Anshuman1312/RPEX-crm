import { createApi } from "@reduxjs/toolkit/query/react";
import { axiosBaseQuery } from "@/core/api/axiosBaseQuery";

export const rootApi = createApi({
  reducerPath: "rootApi",
  baseQuery: axiosBaseQuery(),
  tagTypes: [
    "Auth",
    "Dashboard",
    "Leads",
    "Campaigns",
    "Followups",
    "Customers",
    "Projects",
    "Inventory",
    "Bookings",
    "Payments",
    "Tasks",
    "Meetings",
    "Calendar",
    "Notifications",
    "Reports",
    "Employees",
    "Organizations",
    "Roles",
    "Permissions",
    "Activity",
    "Workflow",
    "Settings"
  ],
  endpoints: () => ({})
});
