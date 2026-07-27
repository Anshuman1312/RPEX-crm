import { PropsWithChildren, useEffect, useRef } from "react";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { toast, Toaster } from "sonner";
import { persistor, store } from "@/app/store";
import { ErrorBoundary } from "@/core/errors/ErrorBoundary";
import { useAppDispatch, useAppSelector } from "@/hooks/redux";
import {
  bindAuthEvents,
  bootstrapAuthSession,
  requestTokenRefresh
} from "@/features/auth/services/authLifecycle";
import { useThemeSync } from "@/core/theme/useThemeSync";

function BootstrapEffects() {
  const dispatch = useAppDispatch();
  const { accessToken, refreshToken, status } = useAppSelector(state => state.auth);
  const previousStatus = useRef(status);

  useThemeSync();

  useEffect(() => {
    bootstrapAuthSession(dispatch);
    const unbind = bindAuthEvents(dispatch);

    return () => {
      unbind();
    };
  }, [dispatch]);

  useEffect(() => {
    if (previousStatus.current === "authenticated" && status === "unauthenticated") {
      toast.error("Your session has expired. Please sign in again.");
    }

    previousStatus.current = status;
  }, [status]);

  useEffect(() => {
    if (!accessToken || !refreshToken) {
      return;
    }

    const intervalId = window.setInterval(() => {
      void requestTokenRefresh();
    }, 5 * 60 * 1000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [accessToken, refreshToken]);

  return null;
}

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <BootstrapEffects />
        <ErrorBoundary>{children}</ErrorBoundary>
        <Toaster richColors closeButton position="top-right" />
      </PersistGate>
    </Provider>
  );
}
