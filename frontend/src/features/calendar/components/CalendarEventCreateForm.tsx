import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { calendarEventTypeOptions } from "@/features/calendar/constants/calendarOptions";
import {
  CreateCalendarEventFormValues,
  createCalendarEventSchema
} from "@/features/calendar/validation/calendarSchemas";

interface CalendarEventCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateCalendarEventFormValues) => Promise<void>;
}

export function CalendarEventCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: CalendarEventCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateCalendarEventFormValues>({
    resolver: zodResolver(createCalendarEventSchema),
    defaultValues: {
      title: "",
      type: "Meeting",
      owner: "",
      attendee: "",
      eventAt: "",
      location: "",
      linkedModule: ""
    }
  });

  return (
    <FormSection
      description="Schedule calendar events with ownership, attendees, and linked module context."
      title="Create Calendar Event"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.title?.message} id="event-title" label="Title" required>
          <Input id="event-title" {...register("title")} />
        </FormField>

        <FormField error={errors.type?.message} id="event-type" label="Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="event-type"
            {...register("type")}
          >
            {calendarEventTypeOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.owner?.message} id="event-owner" label="Owner" required>
          <Input id="event-owner" {...register("owner")} />
        </FormField>

        <FormField error={errors.attendee?.message} id="event-attendee" label="Attendee" required>
          <Input id="event-attendee" {...register("attendee")} />
        </FormField>

        <FormField error={errors.eventAt?.message} id="event-at" label="Event At" required>
          <Input id="event-at" type="datetime-local" {...register("eventAt")} />
        </FormField>

        <FormField error={errors.location?.message} id="event-location" label="Location" required>
          <Input id="event-location" {...register("location")} />
        </FormField>

        <FormField error={errors.linkedModule?.message} id="event-module" label="Linked Module" required>
          <Input id="event-module" {...register("linkedModule")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Event"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
