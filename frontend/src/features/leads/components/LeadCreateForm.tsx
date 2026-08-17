import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, Input } from "@/components";
import {
  leadPriorityOptions,
  leadSourceOptions,
  leadStatusOptions
} from "@/features/leads/constants/leadOptions";
import { CreateLeadFormValues, createLeadSchema } from "@/features/leads/validation/leadSchemas";
import { useAppSelector } from "@/hooks/redux";

interface LeadCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateLeadFormValues) => Promise<void>;
  initialValues?: CreateLeadFormValues;
}

export function LeadCreateForm({
  isSubmitting,
  onCancel,
  onSubmit,
  initialValues
}: LeadCreateFormProps) {
  const session = useAppSelector((state) => state.auth.session);

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateLeadFormValues>({
    resolver: zodResolver(createLeadSchema),
    defaultValues: initialValues || {
      fullName: "",
      email: "",
      phone: "",
      source: "Website",
      priority: "Warm",
      assignedToUserId: session?.userId || "",
      budget: 0,
      nextFollowupAt: "",
      status: "New"
    }
  });

  return (
    <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
      <FormField error={errors.fullName?.message} id="lead-name" label="Lead Name" required>
        <Input id="lead-name" {...register("fullName")} />
      </FormField>

      <FormField error={errors.email?.message} id="lead-email" label="Email" required>
        <Input id="lead-email" type="email" {...register("email")} />
      </FormField>

      <FormField error={errors.phone?.message} id="lead-phone" label="Phone" required>
        <Input id="lead-phone" {...register("phone")} />
      </FormField>

      <FormField error={errors.assignedToUserId?.message} id="lead-owner" label="Owner" required>
        <Input id="lead-owner" readOnly value={session?.name || "System Admin"} />
        <input type="hidden" {...register("assignedToUserId")} />
      </FormField>

      <FormField error={errors.source?.message} id="lead-source" label="Source" required>
        <select
          className="h-10 w-full rounded-md border bg-background px-3 text-sm"
          id="lead-source"
          {...register("source")}
        >
          {leadSourceOptions
            .filter((option) => option !== "All")
            .map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
        </select>
      </FormField>

      <FormField error={errors.priority?.message} id="lead-priority" label="Priority" required>
        <select
          className="h-10 w-full rounded-md border bg-background px-3 text-sm"
          id="lead-priority"
          {...register("priority")}
        >
          {leadPriorityOptions
            .filter((option) => option !== "All")
            .map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
        </select>
      </FormField>

      <FormField error={errors.status?.message} id="lead-status" label="Status" required>
        <select
          className="h-10 w-full rounded-md border bg-background px-3 text-sm"
          id="lead-status"
          {...register("status")}
        >
          {leadStatusOptions
            .filter((option) => option !== "All")
            .map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
        </select>
      </FormField>

      <FormField error={errors.budget?.message} id="lead-budget" label="Budget" required>
        <Input id="lead-budget" type="number" {...register("budget", { valueAsNumber: true })} />
      </FormField>

      <FormField
        error={errors.nextFollowupAt?.message}
        id="lead-followup"
        label="Next Follow-up"
        required
      >
        <Input id="lead-followup" type="date" {...register("nextFollowupAt")} />
      </FormField>

      <div className="col-span-full flex justify-end gap-2">
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
              : "Create Lead"}
        </Button>
      </div>
    </form>
  );
}
