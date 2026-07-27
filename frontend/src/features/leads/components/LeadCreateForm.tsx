import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { leadPriorityOptions, leadSourceOptions, leadStageOptions } from "@/features/leads/constants/leadOptions";
import {
  CreateLeadFormValues,
  createLeadSchema
} from "@/features/leads/validation/leadSchemas";

interface LeadCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateLeadFormValues) => Promise<void>;
}

export function LeadCreateForm({ isSubmitting, onCancel, onSubmit }: LeadCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateLeadFormValues>({
    resolver: zodResolver(createLeadSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      source: "Website",
      priority: "Warm",
      owner: "",
      budget: 0,
      nextFollowUp: "",
      stage: "New"
    }
  });

  return (
    <FormSection description="Capture lead profile, ownership, and follow-up schedule." title="Create Lead">
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="lead-name" label="Lead Name" required>
          <Input id="lead-name" {...register("name")} />
        </FormField>

        <FormField error={errors.email?.message} id="lead-email" label="Email" required>
          <Input id="lead-email" type="email" {...register("email")} />
        </FormField>

        <FormField error={errors.phone?.message} id="lead-phone" label="Phone" required>
          <Input id="lead-phone" {...register("phone")} />
        </FormField>

        <FormField error={errors.owner?.message} id="lead-owner" label="Owner" required>
          <Input id="lead-owner" {...register("owner")} />
        </FormField>

        <FormField error={errors.source?.message} id="lead-source" label="Source" required>
          <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" id="lead-source" {...register("source")}>
            {leadSourceOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.priority?.message} id="lead-priority" label="Priority" required>
          <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" id="lead-priority" {...register("priority")}>
            {leadPriorityOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.stage?.message} id="lead-stage" label="Stage" required>
          <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" id="lead-stage" {...register("stage")}>
            {leadStageOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.budget?.message} id="lead-budget" label="Budget" required>
          <Input id="lead-budget" type="number" {...register("budget", { valueAsNumber: true })} />
        </FormField>

        <FormField error={errors.nextFollowUp?.message} id="lead-followup" label="Next Follow-up" required>
          <Input id="lead-followup" type="date" {...register("nextFollowUp")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Lead"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
