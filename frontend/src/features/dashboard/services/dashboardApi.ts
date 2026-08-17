import { rootApi } from "@/core/api/rootApi";

export interface DashboardKpiLeads {
  total_leads: number;
  new_leads: number;
  qualified_leads: number;
  warm_leads: number;
}

export interface DashboardKpiCampaigns {
  total_campaigns: number;
  active_campaigns: number;
  upcoming_campaigns: number;
  ended_campaigns: number;
}

export interface DashboardKpiCustomers {
  total_customers: number;
  active_customers: number;
  inactive_customers: number;
  blacklisted_customers: number;
}

export interface DashboardKpiFollowups {
  total_followups: number;
  scheduled_followups: number;
  completed_followups: number;
  overdue_followups: number;
}

export interface DashboardKpiProjects {
  total_projects: number;
  planning_projects: number;
  ongoing_projects: number;
  completed_projects: number;
}

export interface DashboardKpiOverview {
  leads: DashboardKpiLeads;
  campaigns: DashboardKpiCampaigns;
  customers: DashboardKpiCustomers;
  followups: DashboardKpiFollowups;
  projects: DashboardKpiProjects;
}

export interface LeadPipelineKpis {
  total_leads: number;
  open_leads: number;
  follow_leads: number;
  visit_scheduled: number;
  visited_leads: number;
  booking_leads: number;
  lost_leads: number;
  inactive_leads: number;
}

export const dashboardApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getDashboardKpis: builder.query<DashboardKpiOverview, void>({
      query: () => ({
        url: "/dashboard/kpis/overview",
        method: "GET"
      }),
      transformResponse: (response: { data: DashboardKpiOverview }) => response.data,
      providesTags: [{ type: "Dashboard", id: "KPIs" }]
    }),
    getDashboardLeadKpis: builder.query<LeadPipelineKpis, void>({
      query: () => ({
        url: "/dashboard/kpis/leads",
        method: "GET"
      }),
      transformResponse: (response: { data: LeadPipelineKpis }) => response.data,
      providesTags: [{ type: "Dashboard", id: "LeadKPIs" }]
    })
  })
});

export const { useGetDashboardKpisQuery, useGetDashboardLeadKpisQuery } = dashboardApi;
