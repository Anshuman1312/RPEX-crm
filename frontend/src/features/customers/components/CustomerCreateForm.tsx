import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, Input } from "@/components";
import { Textarea } from "@/components/ui/textarea";
import {
  CreateCustomerFormValues,
  createCustomerSchema
} from "@/features/customers/validation/customerSchemas";

interface CustomerCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateCustomerFormValues) => Promise<void>;
}

export function CustomerCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: CustomerCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateCustomerFormValues>({
    resolver: zodResolver(createCustomerSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      alternate_phone: "",
      company_name: "",
      customer_type: "individual",
      referred_by_user_id: "",
      lead_converted_from_id: "",
      preferred_contact_method: "",
      preferred_language: "en",
      gstin: "",
      pan: "",
      notes: ""
    }
  });

  return (
    <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.first_name?.message} id="customer-first-name" label="First Name" required>
          <Input id="customer-first-name" {...register("first_name")} />
        </FormField>

        <FormField error={errors.last_name?.message} id="customer-last-name" label="Last Name" required>
          <Input id="customer-last-name" {...register("last_name")} />
        </FormField>

        <FormField error={errors.phone?.message} id="customer-phone" label="Mobile Number (Primary)" required>
          <Input id="customer-phone" {...register("phone")} />
        </FormField>

        <FormField error={errors.alternate_phone?.message} id="customer-alt-phone" label="Alternate Mobile Number">
          <Input id="customer-alt-phone" {...register("alternate_phone")} />
        </FormField>

        <FormField error={errors.email?.message} id="customer-email" label="Email ID" required>
          <Input id="customer-email" type="email" {...register("email")} />
        </FormField>

        <FormField error={errors.company_name?.message} id="customer-company" label="Company Name">
          <Input id="customer-company" {...register("company_name")} />
        </FormField>

        <FormField error={errors.customer_type?.message} id="customer-type" label="Customer Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm capitalize"
            id="customer-type"
            {...register("customer_type")}
          >
            <option value="individual">Individual</option>
            <option value="corporate">Corporate</option>
            <option value="partnership">Partnership</option>
            <option value="trust">Trust</option>
            <option value="nri">NRI</option>
          </select>
        </FormField>

        <FormField error={errors.preferred_contact_method?.message} id="customer-contact-method" label="Preferred Contact Method">
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm capitalize"
            id="customer-contact-method"
            {...register("preferred_contact_method")}
          >
            <option value="">Select Method</option>
            <option value="phone">Phone</option>
            <option value="email">Email</option>
            <option value="whatsapp">WhatsApp</option>
          </select>
        </FormField>

        <FormField error={errors.preferred_language?.message} id="customer-language" label="Preferred Language">
          <Input id="customer-language" {...register("preferred_language")} />
        </FormField>

        <FormField error={errors.gstin?.message} id="customer-gstin" label="GSTIN">
          <Input id="customer-gstin" {...register("gstin")} />
        </FormField>

        <FormField error={errors.pan?.message} id="customer-pan" label="PAN">
          <Input id="customer-pan" {...register("pan")} />
        </FormField>

        <FormField error={errors.referred_by_user_id?.message} id="customer-referred-by" label="Referred By User ID">
          <Input id="customer-referred-by" {...register("referred_by_user_id")} />
        </FormField>

        <FormField error={errors.lead_converted_from_id?.message} id="customer-lead-converted-from" label="Converted From Lead ID">
          <Input id="customer-lead-converted-from" {...register("lead_converted_from_id")} />
        </FormField>

        <div className="sm:col-span-2">
          <FormField error={errors.notes?.message} id="customer-notes" label="Notes">
            <Textarea id="customer-notes" {...register("notes")} />
          </FormField>
        </div>

        <div className="col-span-full flex justify-end gap-2 mt-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Client"}
          </Button>
        </div>
    </form>
  );
}
