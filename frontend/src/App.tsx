import { useEffect } from "react";
import { useSelector } from "react-redux";
import { Navigate, Route, Routes } from "react-router-dom";

import LoginPage from "./auth/LoginPage";
import RegisterPage from "./auth/RegisterPage";
import CampaignsPage from "./campaigns/CampaignsPage";
import { AppShell } from "./components/AppShell";
import CustomersPage from "./customers/CustomersPage";
import DashboardPage from "./dashboard/DashboardPage";
import DocumentsPage from "./documents/DocumentsPage";
import FinancePage from "./finance/FinancePage";
import FollowupsPage from "./leads/FollowupsPage";
import LeadsPage from "./leads/LeadsPage";
import PartnerPortalPage from "./partner/PartnerPortalPage";
import KeywordsPage from "./reports/KeywordsPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import ReportsPage from "./reports/ReportsPage";
import SalesPage from "./sales/SalesPage";
import { api } from "./services/api";
import { RootState } from "./store";

function getDefaultRoute(role: RootState["auth"]["role"]) {
  if (role === "CHANNEL_PARTNER") {
    return "/partner";
  }

  return "/dashboard";
}

export default function App() {
  const { accessToken, role } = useSelector((state: RootState) => state.auth);
  const isAuthenticated = Boolean(accessToken && role);
  const defaultRoute = getDefaultRoute(role);

  useEffect(() => {
    if (accessToken) {
      api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
      return;
    }
    delete api.defaults.headers.common.Authorization;
  }, [accessToken]);

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to={defaultRoute} replace /> : <LoginPage />} />
      <Route path="/partner/login" element={isAuthenticated ? <Navigate to={defaultRoute} replace /> : <LoginPage partnerMode />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to={defaultRoute} replace /> : <RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to={defaultRoute} replace />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SEO_MANAGER", "SALES", "ANALYST", "SUPER_ADMIN", "DIRECTOR", "PROJECT_HEAD", "MARKETING_MANAGER", "SALES_MANAGER", "SALES_EXECUTIVE", "TELECALLER", "CRM_EXECUTIVE", "FINANCE", "LEGAL", "HR", "RECEPTIONIST", "DEVELOPER"]}>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SEO_MANAGER", "SALES", "ANALYST", "SUPER_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE", "TELECALLER", "CRM_EXECUTIVE", "RECEPTIONIST", "DIRECTOR", "PROJECT_HEAD"]}>
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
        <Route
          path="/customers"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SUPER_ADMIN", "CRM_EXECUTIVE", "SALES_MANAGER", "RECEPTIONIST"]}>
              <CustomersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sales"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SUPER_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE", "PROJECT_HEAD", "DIRECTOR"]}>
              <SalesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/finance"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SUPER_ADMIN", "FINANCE", "DIRECTOR"]}>
              <FinancePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <ProtectedRoute allowedRoles={["ADMIN", "SUPER_ADMIN", "LEGAL", "CRM_EXECUTIVE"]}>
              <DocumentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/partner"
          element={
            <ProtectedRoute allowedRoles={["CHANNEL_PARTNER", "ADMIN", "SUPER_ADMIN"]}>
              <PartnerPortalPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to={isAuthenticated ? defaultRoute : "/login"} replace />} />
    </Routes>
  );
}
