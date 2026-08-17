import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { useGetRolesQuery } from "@/features/roles/services/roleApi";
import {
  CreateEmployeeFormValues,
  createEmployeeSchema
} from "@/features/employees/validation/employeeSchemas";

interface EmployeeCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateEmployeeFormValues) => Promise<void>;
}

export function EmployeeCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: EmployeeCreateFormProps) {
  const { data: rolesData } = useGetRolesQuery();
  const roles = rolesData?.items || [];

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateEmployeeFormValues>({
    resolver: zodResolver(createEmployeeSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
      phone: "",
      roleId: ""
    }
  });

  return (
    <FormSection
      description="Register employee profiles with role context."
      title="Create Employee"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.fullName?.message} id="employee-name" label="Full Name" required>
          <Input id="employee-name" {...register("fullName")} />
        </FormField>

        <FormField error={errors.email?.message} id="employee-email" label="Email" required>
          <Input id="employee-email" type="email" {...register("email")} />
        </FormField>

        <FormField error={errors.password?.message} id="employee-password" label="Password" required>
          <Input id="employee-password" type="password" {...register("password")} />
        </FormField>

        <FormField error={errors.phone?.message} id="employee-phone" label="Phone Number" required>
          <Input id="employee-phone" {...register("phone")} />
        </FormField>

        <FormField error={errors.roleId?.message} id="employee-role" label="Role" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="employee-role"
            {...register("roleId")}
          >
            <option value="">Select Role</option>
            {roles.map(option => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Employee"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
