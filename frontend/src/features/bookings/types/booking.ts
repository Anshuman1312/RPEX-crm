export interface BookingRecord {
  id: string;
  bookingInterested: string;
  bookingAmount: number;
  preferredPaymentMode: string;
  financeRequired: boolean;
  loanAssistanceRequired: boolean;
}

export interface BookingFilters {
  search?: string;
  financeRequired?: "All" | "Yes" | "No";
  loanAssistanceRequired?: "All" | "Yes" | "No";
}

export interface BookingStats {
  total: number;
  financeRequired: number;
  loanAssistanceRequired: number;
  totalAmount: number;
}

export interface BookingListResponse {
  items: BookingRecord[];
  total: number;
  stats: BookingStats;
}

export interface CreateBookingInput {
  bookingInterested: string;
  bookingAmount: number;
  preferredPaymentMode: string;
  financeRequired: boolean;
  loanAssistanceRequired: boolean;
}
