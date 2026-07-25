import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
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
      title: "Mr.",
      name: "",
      phone: "",
      alternatePhone: "",
      email: "",
      occupation: "",
      address: "",
      budgetRange: "",
      timeDuration: "",
      purpose: "Self Use",
      propertyType: "Flat",
      remarks: ""
    }
  });

  return (
    <FormSection
      description="Create client profile and capture detailed property preferences."
      title="Create Client Details"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.title?.message} id="customer-title" label="Title" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="customer-title"
            {...register("title")}
          >
            <option value="Mr.">Mr.</option>
            <option value="Miss">Miss</option>
            <option value="Mrs">Mrs</option>
          </select>
        </FormField>

        <FormField error={errors.name?.message} id="customer-name" label="Full Name" required>
          <Input id="customer-name" {...register("name")} />
        </FormField>

        <FormField error={errors.phone?.message} id="customer-phone" label="Mobile Number (Primary)" required>
          <Input id="customer-phone" {...register("phone")} />
        </FormField>

        <FormField error={errors.alternatePhone?.message} id="customer-alt-phone" label="Alternate Mobile Number">
          <Input id="customer-alt-phone" {...register("alternatePhone")} />
        </FormField>

        <FormField error={errors.email?.message} id="customer-email" label="Email ID">
          <Input id="customer-email" type="email" {...register("email")} />
        </FormField>

        <FormField error={errors.occupation?.message} id="customer-occupation" label="Occupation">
          <Input id="customer-occupation" {...register("occupation")} />
        </FormField>

        <FormField error={errors.address?.message} id="customer-address" label="Address" className="sm:col-span-2">
          <Input id="customer-address" {...register("address")} />
        </FormField>

        <FormField error={errors.budgetRange?.message} id="customer-budget" label="Budget Range">
          <Input id="customer-budget" {...register("budgetRange")} placeholder="e.g. 50L - 80L, 1Cr+" />
        </FormField>

        <FormField error={errors.timeDuration?.message} id="customer-duration" label="Time Duration">
          <Input id="customer-duration" {...register("timeDuration")} placeholder="e.g. Immediate, 3 Months" />
        </FormField>

        <FormField error={errors.purpose?.message} id="customer-purpose" label="Purpose" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="customer-purpose"
            {...register("purpose")}
          >
            <option value="Investment">Investment</option>
            <option value="Self Use">Self Use</option>
            <option value="Business">Business</option>
          </select>
        </FormField>

        <FormField error={errors.propertyType?.message} id="customer-property" label="Property Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="customer-property"
            {...register("propertyType")}
          >
            <option value="Plot">Plot</option>
            <option value="Villa">Villa</option>
            <option value="Flat">Flat</option>
            <option value="Commercial">Commercial</option>
          </select>
        </FormField>

        <FormField error={errors.remarks?.message} id="customer-remarks" label="Remarks" className="sm:col-span-2">
          <Input id="customer-remarks" {...register("remarks")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2 mt-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Client"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
