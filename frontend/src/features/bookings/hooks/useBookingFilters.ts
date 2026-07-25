import { useMemo, useState } from "react";
import { BookingFilters } from "@/features/bookings/types/booking";

export function useBookingFilters() {
  const [search, setSearch] = useState("");
  const [financeRequired, setFinanceRequired] = useState<"All" | "Yes" | "No">("All");
  const [loanAssistanceRequired, setLoanAssistanceRequired] = useState<"All" | "Yes" | "No">("All");

  const filters = useMemo<BookingFilters>(
    () => ({
      search,
      financeRequired,
      loanAssistanceRequired
    }),
    [financeRequired, search, loanAssistanceRequired]
  );

  return {
    filters,
    search,
    financeRequired,
    loanAssistanceRequired,
    setSearch,
    setFinanceRequired,
    setLoanAssistanceRequired
  };
}
