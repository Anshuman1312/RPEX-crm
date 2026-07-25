import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { roleScopeOptions } from "@/features/roles/constants/roleOptions";
import { CreateRoleFormValues, createRoleSchema } from "@/features/roles/validation/roleSchemas";

interface Props {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateRoleFormValues) => Promise<void>;
}

export function RoleCreateForm({ isSubmitting, onCancel, onSubmit }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateRoleFormValues>({
    resolver: zodResolver(createRoleSchema),
    defaultValues: { name: "", scope: "Organization", description: "" }
  });

  return (
    <FormSection
      description="Define a new access role with scope and description."
      title="Create Role"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="role-name" label="Role Name" required>
          <Input id="role-name" {...register("name")} />
        </FormField>

        <FormField error={errors.scope?.message} id="role-scope" label="Scope" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="role-scope"
            {...register("scope")}
          >
            {roleScopeOptions.filter(o => o !== "All").map(o => (
              <option key={o} value={o}>{o}</option>
            ))}
          </select>
        </FormField>

        <div className="col-span-full">
          <FormField error={errors.description?.message} id="role-description" label="Description" required>
            <Input id="role-description" {...register("description")} />
          </FormField>
        </div>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">Cancel</Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Role"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
