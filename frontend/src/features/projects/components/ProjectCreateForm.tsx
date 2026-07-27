import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { projectPhaseOptions } from "@/features/projects/constants/projectOptions";
import {
  CreateProjectFormValues,
  createProjectSchema
} from "@/features/projects/validation/projectSchemas";

interface ProjectCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateProjectFormValues) => Promise<void>;
}

export function ProjectCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: ProjectCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateProjectFormValues>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      client: "",
      projectManager: "",
      phase: "Planning",
      budget: 0,
      targetHandover: ""
    }
  });

  return (
    <FormSection
      description="Create project profile and assign manager accountability."
      title="Create Project"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="project-name" label="Project Name" required>
          <Input id="project-name" {...register("name")} />
        </FormField>

        <FormField error={errors.client?.message} id="project-client" label="Client" required>
          <Input id="project-client" {...register("client")} />
        </FormField>

        <FormField
          error={errors.projectManager?.message}
          id="project-manager"
          label="Project Manager"
          required
        >
          <Input id="project-manager" {...register("projectManager")} />
        </FormField>

        <FormField error={errors.phase?.message} id="project-phase" label="Phase" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="project-phase"
            {...register("phase")}
          >
            {projectPhaseOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.budget?.message} id="project-budget" label="Budget (INR)" required>
          <Input id="project-budget" min={0} step={100000} type="number" {...register("budget")} />
        </FormField>

        <FormField
          error={errors.targetHandover?.message}
          id="project-handover"
          label="Target Handover"
          required
        >
          <Input id="project-handover" type="date" {...register("targetHandover")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Project"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
