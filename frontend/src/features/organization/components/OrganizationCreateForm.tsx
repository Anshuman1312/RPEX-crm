import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { organizationIndustryOptions } from "@/features/organization/constants/organizationOptions";
import {
  CreateOrganizationFormValues,
  createOrganizationSchema
} from "@/features/organization/validation/organizationSchemas";

interface Props {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateOrganizationFormValues) => Promise<void>;
}

export function OrganizationCreateForm({ isSubmitting, onCancel, onSubmit }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateOrganizationFormValues>({
    resolver: zodResolver(createOrganizationSchema),
    defaultValues: {
      name: "", industry: "Real Estate", primaryContact: "",
      email: "", phone: "", city: "", employeeCount: 1
    }
  });

  return (
    <FormSection
      description="Register an organization profile with industry classification and contact details."
      title="Create Organization"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="org-name" label="Organization Name" required>
          <Input id="org-name" {...register("name")} />
        </FormField>

        <FormField error={errors.industry?.message} id="org-industry" label="Industry" required>
          <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" id="org-industry" {...register("industry")}>
            {organizationIndustryOptions.filter(o => o !== "All").map(o => (
              <option key={o} value={o}>{o}</option>
            ))}
          </select>
        </FormField>

        <FormField error={errors.primaryContact?.message} id="org-contact" label="Primary Contact" required>
          <Input id="org-contact" {...register("primaryContact")} />
        </FormField>

        <FormField error={errors.email?.message} id="org-email" label="Email" required>
          <Input id="org-email" type="email" {...register("email")} />
        </FormField>

        <FormField error={errors.phone?.message} id="org-phone" label="Phone" required>
          <Input id="org-phone" {...register("phone")} />
        </FormField>

        <FormField error={errors.city?.message} id="org-city" label="City" required>
          <Input id="org-city" {...register("city")} />
        </FormField>

        <FormField error={errors.employeeCount?.message} id="org-employees" label="Employee Count" required>
          <Input id="org-employees" min={1} step={1} type="number" {...register("employeeCount")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">Cancel</Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Organization"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
