import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import {
  followUpChannelOptions,
  followUpPriorityOptions
} from "@/features/followups/constants/followupOptions";
import {
  createFollowUpSchema,
  CreateFollowUpFormValues
} from "@/features/followups/validation/followupSchemas";

interface FollowUpCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateFollowUpFormValues) => Promise<void>;
}

export function FollowUpCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: FollowUpCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateFollowUpFormValues>({
    resolver: zodResolver(createFollowUpSchema),
    defaultValues: {
      leadName: "",
      owner: "",
      scheduledAt: "",
      channel: "Call",
      priority: "Medium",
      notes: ""
    }
  });

  return (
    <FormSection
      description="Track and schedule lead follow-ups with channel, priority, and ownership controls."
      title="Create Follow-up"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.leadName?.message} id="followup-lead" label="Lead Name" required>
          <Input id="followup-lead" {...register("leadName")} />
        </FormField>

        <FormField error={errors.owner?.message} id="followup-owner" label="Owner" required>
          <Input id="followup-owner" {...register("owner")} />
        </FormField>

        <FormField
          error={errors.scheduledAt?.message}
          id="followup-scheduled-at"
          label="Next Follow-up Date & Time"
          required
        >
          <Input id="followup-scheduled-at" type="datetime-local" {...register("scheduledAt")} />
        </FormField>

        <FormField error={errors.channel?.message} id="followup-channel" label="Follow-up Mode" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="followup-channel"
            {...register("channel")}
          >
            {followUpChannelOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.priority?.message} id="followup-priority" label="Priority" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="followup-priority"
            {...register("priority")}
          >
            {followUpPriorityOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.notes?.message} id="followup-notes" label="Follow-up Notes" required>
          <Input id="followup-notes" {...register("notes")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Follow-up"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
