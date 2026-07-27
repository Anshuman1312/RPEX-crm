import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import {
  employeeBandOptions,
  employeeDepartmentOptions
} from "@/features/employees/constants/employeeOptions";
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
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateEmployeeFormValues>({
    resolver: zodResolver(createEmployeeSchema),
    defaultValues: {
      fullName: "",
      email: "",
      department: "Sales",
      band: "Associate",
      manager: "",
      joiningDate: ""
    }
  });

  return (
    <FormSection
      description="Register employee profiles with department, reporting manager, and banding context."
      title="Create Employee"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.fullName?.message} id="employee-name" label="Full Name" required>
          <Input id="employee-name" {...register("fullName")} />
        </FormField>

        <FormField error={errors.email?.message} id="employee-email" label="Email" required>
          <Input id="employee-email" type="email" {...register("email")} />
        </FormField>

        <FormField error={errors.department?.message} id="employee-department" label="Department" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="employee-department"
            {...register("department")}
          >
            {employeeDepartmentOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.band?.message} id="employee-band" label="Band" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="employee-band"
            {...register("band")}
          >
            {employeeBandOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </FormField>

        <FormField error={errors.manager?.message} id="employee-manager" label="Manager" required>
          <Input id="employee-manager" {...register("manager")} />
        </FormField>

        <FormField error={errors.joiningDate?.message} id="employee-joining-date" label="Joining Date" required>
          <Input id="employee-joining-date" type="date" {...register("joiningDate")} />
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
