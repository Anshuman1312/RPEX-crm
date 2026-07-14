import { api } from "./api";

export type CurrentUserProfile = {
  id: string;
  name: string;
  email: string;
  role_id: string;
  role: string | null;
  is_active: boolean;
};

export async function fetchCurrentUserProfile() {
  const response = await api.get<CurrentUserProfile>("/auth/me");
  return response.data;
}
