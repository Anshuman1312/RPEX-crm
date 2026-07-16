import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

import { RoleName } from "../auth/authSlice";
import { RootState } from "../store";

type ProtectedRouteProps = {
  children: JSX.Element;
  allowedRoles?: Exclude<RoleName, null>[];
};

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { accessToken, role } = useSelector((state: RootState) => state.auth);
  if (!accessToken || !role) {
    return <Navigate to="/login" replace />;
  }

  if (role === "ADMIN" || role === "SUPER_ADMIN") {
    return children;
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    if (role === "CHANNEL_PARTNER" || role === "CUSTOMER_PORTAL") {
      return <Navigate to="/partner" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
