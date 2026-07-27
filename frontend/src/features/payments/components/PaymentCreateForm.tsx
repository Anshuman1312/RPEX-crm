import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { paymentMethodOptions } from "@/features/payments/constants/paymentOptions";
import {
  CreatePaymentFormValues,
  createPaymentSchema
} from "@/features/payments/validation/paymentSchemas";

interface PaymentCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreatePaymentFormValues) => Promise<void>;
}

export function PaymentCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: PaymentCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreatePaymentFormValues>({
    resolver: zodResolver(createPaymentSchema),
    defaultValues: {
      bookingId: "",
      customerName: "",
      projectName: "",
      amount: 0,
      method: "UPI",
      transactionDate: "",
      owner: ""
    }
  });

  return (
    <FormSection
      description="Create payment records for booking reconciliation and tracking."
      title="Create Payment"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.bookingId?.message} id="payment-booking-id" label="Booking ID" required>
          <Input id="payment-booking-id" {...register("bookingId")} />
        </FormField>

        <FormField
          error={errors.customerName?.message}
          id="payment-customer"
          label="Customer Name"
          required
        >
          <Input id="payment-customer" {...register("customerName")} />
        </FormField>

        <FormField
          error={errors.projectName?.message}
          id="payment-project"
          label="Project Name"
          required
        >
          <Input id="payment-project" {...register("projectName")} />
        </FormField>

        <FormField error={errors.amount?.message} id="payment-amount" label="Amount (INR)" required>
          <Input id="payment-amount" min={0} step={100000} type="number" {...register("amount")} />
        </FormField>

        <FormField error={errors.method?.message} id="payment-method" label="Method" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="payment-method"
            {...register("method")}
          >
            {paymentMethodOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField
          error={errors.transactionDate?.message}
          id="payment-transaction-date"
          label="Transaction Date"
          required
        >
          <Input id="payment-transaction-date" type="date" {...register("transactionDate")} />
        </FormField>

        <FormField error={errors.owner?.message} id="payment-owner" label="Payment Owner" required>
          <Input id="payment-owner" {...register("owner")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Payment"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
