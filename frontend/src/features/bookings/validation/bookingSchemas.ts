import { z } from "zod";
 
 export const createBookingSchema = z.object({
   bookingInterested: z.string().min(2, "Interested details are required"),
   bookingAmount: z.coerce.number().positive("Booking amount must be greater than zero"),
   preferredPaymentMode: z.string().min(2, "Preferred payment mode is required"),
   financeRequired: z.boolean().default(false),
   loanAssistanceRequired: z.boolean().default(false)
 });
 
 export type CreateBookingFormValues = z.infer<typeof createBookingSchema>;
