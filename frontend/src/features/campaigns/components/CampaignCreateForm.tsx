import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { Textarea } from "@/components/ui/textarea";
import { campaignTypeOptions } from "@/features/campaigns/constants/campaignOptions";
import {
  createCampaignSchema,
  CreateCampaignFormValues
} from "@/features/campaigns/validation/campaignSchemas";

interface CampaignCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateCampaignFormValues) => Promise<void>;
}

export function CampaignCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: CampaignCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateCampaignFormValues>({
    resolver: zodResolver(createCampaignSchema),
    defaultValues: {
      name: "",
      type: "WhatsApp",
      platform: "",
      budget: 1000,
      start_date: "",
      end_date: "",
      extra_data: ""
    }
  });

  return (
    <FormSection
      description="Create conversion campaigns with channel strategy, platform, owner, and timeline control."
      title="Create Campaign"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="campaign-name" label="Campaign Name" required>
          <Input id="campaign-name" {...register("name")} />
        </FormField>

        <FormField error={errors.type?.message} id="campaign-type" label="Type" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="campaign-type"
            {...register("type")}
          >
            {campaignTypeOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.platform?.message} id="campaign-platform" label="Platform" required>
          <Input id="campaign-platform" placeholder="e.g. Meta, Google, Twilio" {...register("platform")} />
        </FormField>

        <FormField error={errors.budget?.message} id="campaign-budget" label="Budget" required>
          <Input id="campaign-budget" min={1} step={1} type="number" {...register("budget")} />
        </FormField>

        <FormField error={errors.start_date?.message} id="campaign-start" label="Start Date" required>
          <Input id="campaign-start" type="date" {...register("start_date")} />
        </FormField>

        <FormField error={errors.end_date?.message} id="campaign-end" label="End Date" required>
          <Input id="campaign-end" type="date" {...register("end_date")} />
        </FormField>

        <div className="col-span-full">
          <FormField error={errors.extra_data?.message} id="campaign-extra-data" label="Extra Data (JSON Format)">
            <Textarea id="campaign-extra-data" placeholder='{"target_audience": "Past Leads"}' {...register("extra_data")} />
          </FormField>
        </div>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Campaign"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
