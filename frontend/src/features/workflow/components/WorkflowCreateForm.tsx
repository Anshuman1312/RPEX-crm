import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { workflowActionOptions, workflowTriggerOptions } from "@/features/workflow/constants/workflowOptions";
import { CreateWorkflowFormValues, createWorkflowSchema } from "@/features/workflow/validation/workflowSchemas";

interface Props {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateWorkflowFormValues) => Promise<void>;
}

export function WorkflowCreateForm({ isSubmitting, onCancel, onSubmit }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateWorkflowFormValues>({
    resolver: zodResolver(createWorkflowSchema),
    defaultValues: { name: "", trigger: "Lead Created", action: "Send Notification", module: "" }
  });

  return (
    <FormSection
      description="Define automation rules with trigger conditions and resulting actions."
      title="Create Workflow"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="wf-name" label="Workflow Name" required>
          <Input id="wf-name" {...register("name")} />
        </FormField>

        <FormField error={errors.module?.message} id="wf-module" label="Module" required>
          <Input id="wf-module" placeholder="e.g. Leads, Bookings" {...register("module")} />
        </FormField>

        <FormField error={errors.trigger?.message} id="wf-trigger" label="Trigger" required>
          <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" id="wf-trigger" {...register("trigger")}>
            {workflowTriggerOptions.filter(o => o !== "All").map(o => (
              <option key={o} value={o}>{o}</option>
            ))}
          </select>
        </FormField>

        <FormField error={errors.action?.message} id="wf-action" label="Action" required>
          <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" id="wf-action" {...register("action")}>
            {workflowActionOptions.map(o => (
              <option key={o} value={o}>{o}</option>
            ))}
          </select>
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">Cancel</Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Workflow"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
