import { Navigate } from "react-router-dom";

type ProtectedRouteProps = {
  hasAccess: boolean;
  children: JSX.Element;
};

export function ProtectedRoute({ hasAccess, children }: ProtectedRouteProps) {
  if (!hasAccess) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
