import { useEffect } from "react";
import { useSelector } from "react-redux";
import { Route, Routes } from "react-router-dom";

import LoginPage from "./auth/LoginPage";
import DashboardPage from "./dashboard/DashboardPage";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { api } from "./services/api";
import { RootState } from "./store";

export default function App() {
  const { accessToken, role } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (accessToken) {
      api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    }
  }, [accessToken]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute hasAccess={Boolean(accessToken && role)}>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
