import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { taskPriorityOptions } from "@/features/tasks/constants/taskOptions";
import {
  CreateTaskFormValues,
  createTaskSchema
} from "@/features/tasks/validation/taskSchemas";

interface TaskCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateTaskFormValues) => Promise<void>;
}

export function TaskCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: TaskCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateTaskFormValues>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: {
      title: "",
      module: "",
      assignee: "",
      dueDate: "",
      priority: "Medium",
      effortPoints: 1
    }
  });

  return (
    <FormSection
      description="Create execution tasks with ownership, due date, and effort sizing."
      title="Create Task"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.title?.message} id="task-title" label="Title" required>
          <Input id="task-title" {...register("title")} />
        </FormField>

        <FormField error={errors.module?.message} id="task-module" label="Module" required>
          <Input id="task-module" {...register("module")} />
        </FormField>

        <FormField error={errors.assignee?.message} id="task-assignee" label="Assignee" required>
          <Input id="task-assignee" {...register("assignee")} />
        </FormField>

        <FormField error={errors.dueDate?.message} id="task-due-date" label="Due Date" required>
          <Input id="task-due-date" type="date" {...register("dueDate")} />
        </FormField>

        <FormField error={errors.priority?.message} id="task-priority" label="Priority" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="task-priority"
            {...register("priority")}
          >
            {taskPriorityOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.effortPoints?.message} id="task-effort" label="Effort Points" required>
          <Input id="task-effort" min={1} step={1} type="number" {...register("effortPoints")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Task"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
