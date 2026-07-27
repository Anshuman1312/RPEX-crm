import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import { campaignChannelOptions } from "@/features/campaigns/constants/campaignOptions";
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
      channel: "WhatsApp",
      owner: "",
      budget: 1000,
      startDate: "",
      endDate: ""
    }
  });

  return (
    <FormSection
      description="Create conversion campaigns with channel strategy, owners, and timeline control."
      title="Create Campaign"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.name?.message} id="campaign-name" label="Campaign Name" required>
          <Input id="campaign-name" {...register("name")} />
        </FormField>

        <FormField error={errors.channel?.message} id="campaign-channel" label="Channel" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="campaign-channel"
            {...register("channel")}
          >
            {campaignChannelOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.owner?.message} id="campaign-owner" label="Owner" required>
          <Input id="campaign-owner" {...register("owner")} />
        </FormField>

        <FormField error={errors.budget?.message} id="campaign-budget" label="Budget" required>
          <Input id="campaign-budget" min={1} step={1} type="number" {...register("budget")} />
        </FormField>

        <FormField error={errors.startDate?.message} id="campaign-start" label="Start Date" required>
          <Input id="campaign-start" type="date" {...register("startDate")} />
        </FormField>

        <FormField error={errors.endDate?.message} id="campaign-end" label="End Date" required>
          <Input id="campaign-end" type="date" {...register("endDate")} />
        </FormField>

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
