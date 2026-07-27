import { useMemo, useState } from "react";
import {
  PaymentFilters,
  PaymentMethod,
  PaymentStatus
} from "@/features/payments/types/payment";

export function usePaymentFilters() {
  const [search, setSearch] = useState("");
  const [method, setMethod] = useState<PaymentMethod | "All">("All");
  const [status, setStatus] = useState<PaymentStatus | "All">("All");

  const filters = useMemo<PaymentFilters>(
    () => ({
      search,
      method,
      status
    }),
    [method, search, status]
  );

  return {
    filters,
    search,
    method,
    status,
    setSearch,
    setMethod,
    setStatus
  };
}
