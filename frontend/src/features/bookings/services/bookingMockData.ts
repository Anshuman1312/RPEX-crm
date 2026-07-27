import {
  BookingListResponse,
  BookingRecord,
  BookingStats,
  CreateBookingInput
} from "@/features/bookings/types/booking";

function formatDate(offset: number) {
  const date = new Date();
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialBookingRecords: BookingRecord[] = [
  {
    id: "BK-5101",
    bookingInterested: "Skyline Heights Phase 2 - 3BHK",
    bookingAmount: 1200000,
    preferredPaymentMode: "Bank Transfer",
    financeRequired: true,
    loanAssistanceRequired: true
  },
  {
    id: "BK-5102",
    bookingInterested: "Riverfront Residency - 2BHK",
    bookingAmount: 900000,
    preferredPaymentMode: "Cheque",
    financeRequired: false,
    loanAssistanceRequired: false
  },
  {
    id: "BK-5103",
    bookingInterested: "Orchid Greens - Villa",
    bookingAmount: 750000,
    preferredPaymentMode: "Cash",
    financeRequired: true,
    loanAssistanceRequired: false
  },
  {
    id: "BK-5104",
    bookingInterested: "Emerald Business Park - Office Space",
    bookingAmount: 650000,
    preferredPaymentMode: "Card",
    financeRequired: false,
    loanAssistanceRequired: false
  }
];

export function buildBookingStats(records: BookingRecord[]): BookingStats {
  return {
    total: records.length,
    financeRequired: records.filter(record => record.financeRequired).length,
    loanAssistanceRequired: records.filter(record => record.loanAssistanceRequired).length,
    totalAmount: records.reduce((sum, record) => sum + record.bookingAmount, 0)
  };
}

export function buildBookingListResponse(records: BookingRecord[]): BookingListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildBookingStats(records)
  };
}

export function createBookingRecord(payload: CreateBookingInput, index: number): BookingRecord {
  return {
    id: `BK-${5100 + index}`,
    bookingInterested: payload.bookingInterested,
    bookingAmount: payload.bookingAmount,
    preferredPaymentMode: payload.preferredPaymentMode,
    financeRequired: payload.financeRequired,
    loanAssistanceRequired: payload.loanAssistanceRequired
  };
}
