import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button, FormField, FormSection, Input } from "@/components";
import {
  inventoryCategoryOptions,
  inventoryStatusOptions
} from "@/features/inventory/constants/inventoryOptions";
import {
  CreateInventoryUnitFormValues,
  createInventoryUnitSchema
} from "@/features/inventory/validation/inventorySchemas";

interface InventoryCreateFormProps {
  isSubmitting: boolean;
  onCancel: () => void;
  onSubmit: (values: CreateInventoryUnitFormValues) => Promise<void>;
}

export function InventoryCreateForm({
  isSubmitting,
  onCancel,
  onSubmit
}: InventoryCreateFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<CreateInventoryUnitFormValues>({
    resolver: zodResolver(createInventoryUnitSchema),
    defaultValues: {
      unitCode: "",
      project: "",
      category: "Apartment",
      status: "Available",
      sizeSqFt: 0,
      price: 0,
      assignedAgent: ""
    }
  });

  return (
    <FormSection
      description="Add inventory units with category, pricing, and ownership assignments."
      title="Create Inventory Unit"
    >
      <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(onSubmit)}>
        <FormField error={errors.unitCode?.message} id="inventory-unit-code" label="Unit Code" required>
          <Input id="inventory-unit-code" {...register("unitCode")} />
        </FormField>

        <FormField error={errors.project?.message} id="inventory-project" label="Project" required>
          <Input id="inventory-project" {...register("project")} />
        </FormField>

        <FormField error={errors.category?.message} id="inventory-category" label="Category" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="inventory-category"
            {...register("category")}
          >
            {inventoryCategoryOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.status?.message} id="inventory-status" label="Status" required>
          <select
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            id="inventory-status"
            {...register("status")}
          >
            {inventoryStatusOptions
              .filter(option => option !== "All")
              .map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
          </select>
        </FormField>

        <FormField error={errors.sizeSqFt?.message} id="inventory-size" label="Size (sq ft)" required>
          <Input id="inventory-size" min={0} step={10} type="number" {...register("sizeSqFt")} />
        </FormField>

        <FormField error={errors.price?.message} id="inventory-price" label="Price (INR)" required>
          <Input id="inventory-price" min={0} step={100000} type="number" {...register("price")} />
        </FormField>

        <FormField
          error={errors.assignedAgent?.message}
          id="inventory-agent"
          label="Assigned Agent"
          required
        >
          <Input id="inventory-agent" {...register("assignedAgent")} />
        </FormField>

        <div className="col-span-full flex justify-end gap-2">
          <Button onClick={onCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create Unit"}
          </Button>
        </div>
      </form>
    </FormSection>
  );
}
