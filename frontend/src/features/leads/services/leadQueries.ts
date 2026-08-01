import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CreateLeadInput,
  LeadFilters,
  LeadListResponse,
  LeadRecord,
  LeadStatus,
  LeadSource,
  LeadPriority,
  LeadStats
} from "@/features/leads/types/lead";
import { http } from "@/core/api/axios";

// Query keys for robust caching and cache invalidation
export const leadKeys = {
  all: ["leads"] as const,
  lists: () => [...leadKeys.all, "list"] as const,
  list: (filters: LeadFilters | void) => [...leadKeys.lists(), { filters }] as const,
  details: () => [...leadKeys.all, "detail"] as const,
  detail: (id: string) => [...leadKeys.details(), id] as const,
};

// Mappers between frontend values and backend values
export const mapStatusToBackend = (status: string): string => {
  switch (status) {
    case "New": return "new";
    case "Qualified": return "qualified";
    case "Negotiation": return "negotiation";
    case "Won": return "converted";
    case "Future Perspective": return "lost";
    default: return status.toLowerCase();
  }
};

export const mapStatusToFrontend = (status: string): string => {
  switch (status.toLowerCase()) {
    case "new":
    case "contacted":
      return "New";
    case "qualified":
      return "Qualified";
    case "proposal_sent":
    case "negotiation":
      return "Negotiation";
    case "converted":
      return "Won";
    case "lost":
    case "inactive":
      return "Future Perspective";
    default:
      return "New";
  }
};

export const mapPriorityToBackend = (priority: string): string => {
  switch (priority) {
    case "Hot": return "high";
    case "Warm": return "medium";
    case "Cold": return "low";
    default: return priority.toLowerCase();
  }
};

export const mapPriorityToFrontend = (priority: string): string => {
  switch (priority.toLowerCase()) {
    case "high":
    case "critical":
      return "Hot";
    case "medium":
      return "Warm";
    case "low":
      return "Cold";
    default:
      return "Warm";
  }
};

export const mapSourceToBackend = (source: string): string => {
  switch (source) {
    case "Facebook":
    case "Instagram":
    case "WhatsApp":
      return "social_media";
    case "Google Ads":
      return "advertisement";
    case "Website":
      return "website";
    case "Walk-in":
      return "walk_in";
    case "Referral":
    case "Client Reference":
      return "referral";
    case "Channel Partner":
      return "agent";
    default:
      return "other";
  }
};

export const mapSourceToFrontend = (source: string): string => {
  switch (source.toLowerCase()) {
    case "social_media":
      return "Facebook";
    case "advertisement":
      return "Google Ads";
    case "website":
      return "Website";
    case "walk_in":
      return "Walk-in";
    case "referral":
      return "Referral";
    case "agent":
      return "Channel Partner";
    default:
      return "Other";
  }
};

export function mapBackendLeadToRecord(lead: any): LeadRecord {
  return {
    id: lead.id,
    fullName: lead.full_name || "",
    email: lead.email || "",
    phone: lead.phone || "",
    source: mapSourceToFrontend(lead.source || "other") as LeadSource,
    status: mapStatusToFrontend(lead.status || "new") as LeadStatus,
    priority: mapPriorityToFrontend(lead.priority || "medium") as LeadPriority,
    assignedToUserId: lead.assigned_to_user_id || "",
    budget: lead.budget || 0,
    nextFollowupAt: lead.next_followup_at ? new Date(lead.next_followup_at).toISOString().slice(0, 10) : "",
    createdAt: lead.created_at ? new Date(lead.created_at).toISOString().slice(0, 10) : new Date().toISOString().slice(0, 10),
  };
}

export function mapBackendStatsToFrontend(statsData: any): LeadStats {
  const byStatus = statsData.by_status || {};
  const newLeads = (byStatus["new"] || 0) + (byStatus["contacted"] || 0);
  const qualified = byStatus["qualified"] || 0;
  const won = byStatus["converted"] || 0;
  
  return {
    total: statsData.total || 0,
    newLeads,
    qualified,
    won
  };
}

// 1. Fetch leads query hook
export function useGetLeadsQuery(filters: LeadFilters | void) {
  return useQuery<LeadListResponse, Error>({
    queryKey: leadKeys.list(filters),
    queryFn: async () => {
      const params: any = {
        page: 1,
        page_size: 100
      };
      
      if (filters) {
        if (filters.search) {
          params.search = filters.search;
        }
        if (filters.status && filters.status !== "All") {
          params.statuses = mapStatusToBackend(filters.status);
        }
        if (filters.source && filters.source !== "All") {
          params.sources = mapSourceToBackend(filters.source);
        }
      }

      // Fetch leads list and stats in parallel
      const [leadsRes, statsRes] = await Promise.all([
        http.get<{ data: any[]; total: number }>("/leads", { params }),
        http.get<{ data: any }>("/leads/stats/overview")
      ]);

      const items = (leadsRes.data.data || []).map(mapBackendLeadToRecord);
      const stats = mapBackendStatsToFrontend(leadsRes.data.data || {});

      return {
        items,
        total: leadsRes.data.total || items.length,
        stats
      };
    },
  });
}

// 2. Create lead mutation hook
export function useCreateLeadMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<LeadRecord, Error, CreateLeadInput>({
    mutationFn: async (payload: CreateLeadInput) => {
      const backendPayload = {
        full_name: payload.fullName,
        email: payload.email || undefined,
        phone: payload.phone || undefined,
        source: mapSourceToBackend(payload.source),
        status: mapStatusToBackend(payload.status || "New"),
        priority: mapPriorityToBackend(payload.priority || "Warm"),
        budget: payload.budget || undefined,
        assigned_to_user_id: payload.assignedToUserId || undefined,
        next_followup_at: payload.nextFollowupAt ? new Date(payload.nextFollowupAt).toISOString() : undefined,
      };

      const response = await http.post<{ data: any }>("/leads", backendPayload);
      return mapBackendLeadToRecord(response.data.data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leadKeys.lists() });
    },
  });

  return [
    mutation.mutateAsync,
    {
      isLoading: mutation.isPending,
      error: mutation.error,
      reset: mutation.reset,
    },
  ] as const;
}

// 3. Update lead status mutation hook
export function useUpdateLeadStatusMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<LeadRecord, Error, { leadId: string; status: LeadStatus }>({
    mutationFn: async ({ leadId, status }) => {
      const backendStatus = mapStatusToBackend(status);
      const response = await http.post<{ data: any }>(`/leads/${leadId}/status`, { status: backendStatus });
      return mapBackendLeadToRecord(response.data.data);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: leadKeys.lists() });
      queryClient.invalidateQueries({ queryKey: leadKeys.detail(data.id) });
    },
  });

  return [
    mutation.mutateAsync,
    {
      isLoading: mutation.isPending,
      error: mutation.error,
      reset: mutation.reset,
    },
  ] as const;
}

// 4. Update lead details mutation hook
export function useUpdateLeadMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<LeadRecord, Error, { leadId: string; payload: Partial<CreateLeadInput> }>({
    mutationFn: async ({ leadId, payload }) => {
      const backendPayload: any = {};
      if (payload.fullName !== undefined) backendPayload.full_name = payload.fullName;
      if (payload.email !== undefined) backendPayload.email = payload.email;
      if (payload.phone !== undefined) backendPayload.phone = payload.phone;
      if (payload.source !== undefined) backendPayload.source = mapSourceToBackend(payload.source);
      if (payload.priority !== undefined) backendPayload.priority = mapPriorityToBackend(payload.priority);
      if (payload.assignedToUserId !== undefined) backendPayload.assigned_to_user_id = payload.assignedToUserId;
      if (payload.budget !== undefined) backendPayload.budget = payload.budget;
      if (payload.status !== undefined) backendPayload.status = mapStatusToBackend(payload.status);
      if (payload.nextFollowupAt !== undefined) {
        backendPayload.next_followup_at = payload.nextFollowupAt ? new Date(payload.nextFollowupAt).toISOString() : null;
      }

      const response = await http.patch<{ data: any }>(`/leads/${leadId}`, backendPayload);
      return mapBackendLeadToRecord(response.data.data);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: leadKeys.lists() });
      queryClient.invalidateQueries({ queryKey: leadKeys.detail(data.id) });
    },
  });

  return [
    mutation.mutateAsync,
    {
      isLoading: mutation.isPending,
      error: mutation.error,
      reset: mutation.reset,
    },
  ] as const;
}

// 5. Delete lead mutation hook
export function useDeleteLeadMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<void, Error, string>({
    mutationFn: async (leadId: string) => {
      await http.delete(`/leads/${leadId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leadKeys.lists() });
    },
  });

  return [
    mutation.mutateAsync,
    {
      isLoading: mutation.isPending,
      error: mutation.error,
      reset: mutation.reset,
    },
  ] as const;
}
