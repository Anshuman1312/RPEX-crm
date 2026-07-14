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

  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
