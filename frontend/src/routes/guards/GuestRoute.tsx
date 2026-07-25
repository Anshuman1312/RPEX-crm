import { Navigate, Outlet } from "react-router-dom";
import { useAppSelector } from "@/hooks/redux";
import { appPaths } from "@/routes/config/paths";

export function GuestRoute() {
  const { accessToken, status } = useAppSelector(state => state.auth);

  if (status === "unknown") {
    return null;
  }

  if (accessToken) {
    return <Navigate to={appPaths.dashboard} replace />;
  }

  return <Outlet />;
}
