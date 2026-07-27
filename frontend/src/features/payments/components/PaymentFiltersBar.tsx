import { SearchInput } from "@/components";
import {
  paymentMethodOptions,
  paymentStatusOptions
} from "@/features/payments/constants/paymentOptions";
import {
  PaymentMethod,
  PaymentStatus
} from "@/features/payments/types/payment";

interface PaymentFiltersBarProps {
  search: string;
  method: PaymentMethod | "All";
  status: PaymentStatus | "All";
  onSearchChange: (value: string) => void;
  onMethodChange: (value: PaymentMethod | "All") => void;
  onStatusChange: (value: PaymentStatus | "All") => void;
}

export function PaymentFiltersBar({
  search,
  method,
  status,
  onSearchChange,
  onMethodChange,
  onStatusChange
}: PaymentFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by payment id, booking, customer, project, owner"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onMethodChange(event.target.value as PaymentMethod | "All")}
        value={method}
      >
        {paymentMethodOptions.map(option => (
          <option key={option} value={option}>
            Method: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as PaymentStatus | "All")}
        value={status}
      >
        {paymentStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
