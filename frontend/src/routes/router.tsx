import { lazy } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { EnterpriseLayout } from "@/layouts/EnterpriseLayout";
import { RouteSuspense } from "@/routes/components/RouteSuspense";
import { moduleRouteCatalog } from "@/routes/config/moduleRoutes";
import { appPaths } from "@/routes/config/paths";
import { GuestRoute } from "@/routes/guards/GuestRoute";
import { ProtectedRoute } from "@/routes/guards/ProtectedRoute";

const LoginPage = lazy(async () => {
  const module = await import("@/features/auth/pages/LoginPage");
  return { default: module.LoginPage };
});

const ForbiddenPage = lazy(async () => {
  const module = await import("@/pages/errors/ForbiddenPage");
  return { default: module.ForbiddenPage };
});

const NotFoundPage = lazy(async () => {
  const module = await import("@/pages/errors/NotFoundPage");
  return { default: module.NotFoundPage };
});

const protectedModuleRoutes = moduleRouteCatalog.map(route => {
  const PageComponent = route.component;

  return {
    path: route.path.replace(/^\//, ""),
    element: <ProtectedRoute requiredPermission={route.permission} />,
    children: [
      {
        index: true,
        element: (
          <RouteSuspense>
            <PageComponent />
          </RouteSuspense>
        )
      }
    ]
  };
});

export const router = createBrowserRouter([
  {
    path: appPaths.authBase,
    element: <GuestRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          {
            path: "login",
            element: (
              <RouteSuspense>
                <LoginPage />
              </RouteSuspense>
            )
          }
        ]
      },
      { path: "*", element: <Navigate replace to={appPaths.login} /> }
    ]
  },
  {
    path: appPaths.root,
    element: <ProtectedRoute />,
    children: [
      {
        element: <EnterpriseLayout />,
        children: [
          { index: true, element: <Navigate replace to={appPaths.dashboard} /> },
          ...protectedModuleRoutes
        ]
      },
      {
        path: appPaths.forbidden.replace(/^\//, ""),
        element: (
          <RouteSuspense>
            <ForbiddenPage />
          </RouteSuspense>
        )
      }
    ]
  },
  {
    path: "*",
    element: (
      <RouteSuspense>
        <NotFoundPage />
      </RouteSuspense>
    )
  }
]);
