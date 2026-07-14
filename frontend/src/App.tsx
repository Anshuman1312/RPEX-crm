import { useEffect } from "react";
import { useSelector } from "react-redux";
import { Navigate, Route, Routes } from "react-router-dom";

import LoginPage from "./auth/LoginPage";
import RegisterPage from "./auth/RegisterPage";
import CampaignsPage from "./campaigns/CampaignsPage";
import { AppShell } from "./components/AppShell";
import DashboardPage from "./dashboard/DashboardPage";
import FollowupsPage from "./leads/FollowupsPage";
import LeadsPage from "./leads/LeadsPage";
import KeywordsPage from "./reports/KeywordsPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import ReportsPage from "./reports/ReportsPage";
import { api } from "./services/api";
import { RootState } from "./store";

export default function App() {
  const { accessToken, role } = useSelector((state: RootState) => state.auth);
  const isAuthenticated = Boolean(accessToken && role);

  useEffect(() => {
    if (accessToken) {
      api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
      return;
    }
    delete api.defaults.headers.common.Authorization;
  }, [accessToken]);

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SEO_MANAGER", "SALES", "ANALYST"]}>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SEO_MANAGER", "SALES", "ANALYST"]}>
              <LeadsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/campaigns"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SEO_MANAGER"]}>
              <CampaignsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/keywords"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SEO_MANAGER", "ANALYST"]}>
              <KeywordsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/followups"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SALES"]}>
              <FollowupsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "ANALYST"]}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
}
