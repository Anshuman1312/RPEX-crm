import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { reportRangeOptions, reportTypeOptions } from "@/features/reports/constants/reportOptions";
import { CreateReportFormValues, createReportSchema } from "@/features/reports/validation/reportSchemas";

interface ReportCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateReportFormValues) => Promise<void>;
}

export function ReportCreateForm({ isSubmitting, onCancel, onSubmit }: ReportCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateReportFormValues>({
    resolver: zodResolver(createReportSchema),
    defaultValues: {
      title: "",
      type: "Sales",
      range: "This Month",
      owner: ""
    }
  });

  return (
    <FormSection
      description="Create reporting jobs by type and period for analysis and exports."
      title="Create Report"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.title?.message} id="report-title" label="Report Title" required>
          <Input id="report-title" {...register("title")} />
        </FormField>

        <FormField error={errors.type?.message} id="report-type" label="Report Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="report-type"
            {...register("type")}
          >
            {reportTypeOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.range?.message} id="report-range" label="Range" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="report-range"
            {...register("range")}
          >
            {reportRangeOptions.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </FormField>

        <FormField error={errors.owner?.message} id="report-owner" label="Owner" required>
          <Input id="report-owner" {...register("owner")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Report"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
