import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { meetingTypeOptions } from "@/features/meetings/constants/meetingOptions";
import {
  CreateMeetingFormValues,
  createMeetingSchema
} from "@/features/meetings/validation/meetingSchemas";

interface MeetingCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateMeetingFormValues) => Promise<void>;
}

export function MeetingCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: MeetingCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateMeetingFormValues>({
    resolver: zodResolver(createMeetingSchema),
    defaultValues: {
      title: "",
      type: "Client Call",
      host: "",
      attendee: "",
      scheduledAt: "",
      location: "",
      notes: ""
    }
  });

  return (
    <FormSection
      description="Schedule meetings with host ownership, attendee mapping, and context notes."
      title="Create Meeting"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.title?.message} id="meeting-title" label="Title" required>
          <Input id="meeting-title" {...register("title")} />
        </FormField>

        <FormField error={errors.type?.message} id="meeting-type" label="Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="meeting-type"
            {...register("type")}
          >
            {meetingTypeOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.host?.message} id="meeting-host" label="Host" required>
          <Input id="meeting-host" {...register("host")} />
        </FormField>

        <FormField error={errors.attendee?.message} id="meeting-attendee" label="Attendee" required>
          <Input id="meeting-attendee" {...register("attendee")} />
        </FormField>

        <FormField
          error={errors.scheduledAt?.message}
          id="meeting-scheduled"
          label="Scheduled At"
          required
        >
          <Input id="meeting-scheduled" type="datetime-local" {...register("scheduledAt")} />
        </FormField>

        <FormField error={errors.location?.message} id="meeting-location" label="Location" required>
          <Input id="meeting-location" {...register("location")} />
        </FormField>

        <FormField
          error={errors.notes?.message}
          id="meeting-notes"
          label="Notes"
          required
        >
          <Input id="meeting-notes" {...register("notes")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Meeting"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
