import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { notificationTypeOptions } from "@/features/notifications/constants/notificationOptions";
import {
  CreateNotificationFormValues,
  createNotificationSchema
} from "@/features/notifications/validation/notificationSchemas";

interface NotificationCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateNotificationFormValues) => Promise<void>;
}

export function NotificationCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: NotificationCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateNotificationFormValues>({
    resolver: zodResolver(createNotificationSchema),
    defaultValues: {
      title: "",
      message: "",
      type: "Reminder",
      owner: "",
      sourceModule: ""
    }
  });

  return (
    <FormSection
      description="Create in-app notifications with module source and ownership context."
      title="Create Notification"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.title?.message} id="notification-title" label="Title" required>
          <Input id="notification-title" {...register("title")} />
        </FormField>

        <FormField error={errors.type?.message} id="notification-type" label="Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="notification-type"
            {...register("type")}
          >
            {notificationTypeOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.owner?.message} id="notification-owner" label="Owner" required>
          <Input id="notification-owner" {...register("owner")} />
        </FormField>

        <FormField
          error={errors.sourceModule?.message}
          id="notification-source-module"
          label="Source Module"
          required
        >
          <Input id="notification-source-module" {...register("sourceModule")} />
        </FormField>

        <div className="col-span-full">
          <FormField error={errors.message?.message} id="notification-message" label="Message" required>
            <Input id="notification-message" {...register("message")} />
          </FormField>
        </div>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Notification"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
