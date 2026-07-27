import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import {
  CreateBookingFormValues,
  createBookingSchema
} from "@/features/bookings/validation/bookingSchemas";

interface BookingCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateBookingFormValues) => Promise<void>;
}

export function BookingCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: BookingCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateBookingFormValues>({
    resolver: zodResolver(createBookingSchema),
    defaultValues: {
      bookingInterested: "",
      bookingAmount: 0,
      preferredPaymentMode: "",
      financeRequired: false,
      loanAssistanceRequired: false
    }
  });

  return (
    <FormSection
      description="Create and assign new booking entries with interested item and commercial details."
      title="Create Booking"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField
          error={errors.bookingInterested?.message}
          id="booking-interested"
          label="Booking Interested"
          required
        >
          <Input id="booking-interested" {...register("bookingInterested")} />
        </FormField>

        <FormField
          error={errors.bookingAmount?.message}
          id="booking-amount"
          label="Booking Amount (INR)"
          required
        >
          <Input id="booking-amount" min={0} step={100000} type="number" {...register("bookingAmount")} />
        </FormField>

        <FormField
          error={errors.preferredPaymentMode?.message}
          id="booking-payment-mode"
          label="Preferred Payment Mode"
          required
        >
          <select
            id="booking-payment-mode"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            {...register("preferredPaymentMode")}
          >
            <option value="">Select Mode</option>
            <option value="Bank Transfer">Bank Transfer</option>
            <option value="Cheque">Cheque</option>
            <option value="Cash">Cash</option>
            <option value="Card">Card</option>
          </select>
        </FormField>

        <div className="flex flex-col justify-center gap-2 p-2">
          <div className="flex items-center gap-2">
            <input
              id="booking-finance-required"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              {...register("financeRequired")}
            />
            <label htmlFor="booking-finance-required" className="text-sm font-medium leading-none">
              Finance Required
            </label>
          </div>

          <div className="flex items-center gap-2 mt-2">
            <input
              id="booking-loan-assistance"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              {...register("loanAssistanceRequired")}
            />
            <label htmlFor="booking-loan-assistance" className="text-sm font-medium leading-none">
              Loan Assistance Required
            </label>
          </div>
        </div>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Booking"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
