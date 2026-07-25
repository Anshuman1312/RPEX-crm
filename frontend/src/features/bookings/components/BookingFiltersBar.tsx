import { SearchInput } from "@/components";
import {
  financeRequiredOptions,
  loanAssistanceRequiredOptions
} from "@/features/bookings/constants/bookingOptions";

interface BookingFiltersBarProps {
  search: string;
  financeRequired: "All" | "Yes" | "No";
  loanAssistanceRequired: "All" | "Yes" | "No";
  onSearchChange: (value: string) => void;
  onFinanceRequiredChange: (value: "All" | "Yes" | "No") => void;
  onLoanAssistanceRequiredChange: (value: "All" | "Yes" | "No") => void;
}

export function BookingFiltersBar({
  search,
  financeRequired,
  loanAssistanceRequired,
  onSearchChange,
  onFinanceRequiredChange,
  onLoanAssistanceRequiredChange
}: BookingFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by booking id, interested, payment mode..."
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={(event) => onFinanceRequiredChange(event.target.value as "All" | "Yes" | "No")}
        value={financeRequired}
      >
        {financeRequiredOptions.map((option) => (
          <option key={option} value={option}>
            Finance: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={(event) =>
          onLoanAssistanceRequiredChange(event.target.value as "All" | "Yes" | "No")
        }
        value={loanAssistanceRequired}
      >
        {loanAssistanceRequiredOptions.map((option) => (
          <option key={option} value={option}>
            Loan Assistance: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
