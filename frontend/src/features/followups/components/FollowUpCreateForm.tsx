import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, Input } from "@/components";
import { Textarea } from "@/components/ui/textarea";
import { useAppSelector } from "@/hooks/redux";
import {
  followUpTypeOptions,
} from "@/features/followups/constants/followupOptions";
import {
  createFollowUpSchema,
  CreateFollowUpFormValues
} from "@/features/followups/validation/followupSchemas";

interface FollowUpCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateFollowUpFormValues) => Promise<void>;
  initialValues?: CreateFollowUpFormValues;
}

export function FollowUpCreateForm({
  isSubmitting,
  onCancel,
  onSubmit,
  initialValues
}: FollowUpCreateFormProps) {
  const session = useAppSelector((state) => state.auth.session);

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateFollowUpFormValues>({
    resolver: zodResolver(createFollowUpSchema),
    defaultValues: initialValues || {
      type: "call",
      subject: "",
      description: "",
      scheduled_at: "",
      assigned_to_user_id: session?.userId || "",
      lead_id: "",
      customer_id: "",
      priority: 1, // Medium
      is_critical: false,
      notes: ""
    }
  });

  return (
    <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
      <FormField error={errors.subject?.message} id="followup-subject" label="Subject" required>
        <Input id="followup-subject" {...register("subject")} />
      </FormField>

      <FormField error={errors.type?.message} id="followup-type" label="Type" required>
        <select
          className="h-10 w-full rounded-md border bg-background px-3 text-sm capitalize"
          id="followup-type"
          {...register("type")}
        >
          {followUpTypeOptions
            .filter(option => option !== "All")
            .map(option => (
              <option key={option} value={option}>
                {option.replace("_", " ")}
              </option>
            ))}
        </select>
      </FormField>

      <FormField error={errors.description?.message} id="followup-description" label="Description">
        <Input id="followup-description" {...register("description")} />
      </FormField>

      <FormField
        error={errors.scheduled_at?.message}
        id="followup-scheduled-at"
        label="Scheduled Date & Time"
        required
      >
        <Input id="followup-scheduled-at" type="datetime-local" {...register("scheduled_at")} />
      </FormField>

      <FormField error={errors.assigned_to_user_id?.message} id="followup-owner" label="Assigned Owner" required>
        <Input id="followup-owner" readOnly value={session?.name || "System Admin"} />
        <input type="hidden" {...register("assigned_to_user_id")} />
      </FormField>

      <FormField error={errors.priority?.message} id="followup-priority" label="Priority" required>
        <select
          className="h-10 w-full rounded-md border bg-background px-3 text-sm"
          id="followup-priority"
          {...register("priority")}
        >
          <option value={0}>Low</option>
          <option value={1}>Medium</option>
          <option value={2}>High</option>
        </select>
      </FormField>

      <FormField error={errors.lead_id?.message} id="followup-lead-id" label="Lead ID (UUID)">
        <Input id="followup-lead-id" placeholder="Optional" {...register("lead_id")} />
      </FormField>

      <FormField error={errors.customer_id?.message} id="followup-customer-id" label="Customer ID (UUID)">
        <Input id="followup-customer-id" placeholder="Optional" {...register("customer_id")} />
      </FormField>

      <FormField error={errors.is_critical?.message} id="followup-critical" label="Critical Follow-up">
        <select
          className="h-10 w-full rounded-md border bg-background px-3 text-sm"
          id="followup-critical"
          {...register("is_critical", { setValueAsBoolean: true })}
        >
          <option value="false">No</option>
          <option value="true">Yes</option>
        </select>
      </FormField>

      <div className="col-span-full">
        <FormField error={errors.notes?.message} id="followup-notes" label="Follow-up Notes">
          <Textarea id="followup-notes" {...register("notes")} />
        </FormField>
      </div>

      <div className="col-span-full flex justify-end gap-2 mt-2">
        <Button onClick={onCancel} type="button" variant="outline">
          Cancel
        </Button>
        <Button disabled={isSubmitting} type="submit">
          {isSubmitting
            ? initialValues
              ? "Saving..."
              : "Creating..."
            : initialValues
              ? "Save Changes"
              : "Create Follow-up"}
        </Button>
      </div>
    </form>
  );
}
