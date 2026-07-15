import { api } from "./api";

export type CurrentUserProfile = {
  id: string;
  name: string;
  email: string;
  role_id: string;
  role: string | null;
  role_description: string | null;
  is_active: boolean;
  permissions: string[];
};

export async function fetchCurrentUserProfile() {
  const response = await api.get<CurrentUserProfile>("/auth/me");
  return response.data;
}
