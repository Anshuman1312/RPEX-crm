import { z } from "zod";
import {
  inventoryCategoryOptions,
  inventoryStatusOptions
} from "@/features/inventory/constants/inventoryOptions";

export const createInventoryUnitSchema = z.object({
  unitCode: z.string().min(2, "Unit code is required"),
  project: z.string().min(2, "Project name is required"),
  category: z.enum(inventoryCategoryOptions.filter(option => option !== "All") as ["Apartment", "Villa", "Commercial", "Plot"]),
  status: z.enum(inventoryStatusOptions.filter(option => option !== "All") as ["Available", "Reserved", "Sold"]),
  sizeSqFt: z.coerce.number().positive("Size must be greater than zero"),
  price: z.coerce.number().positive("Price must be greater than zero"),
  assignedAgent: z.string().min(2, "Assigned agent is required")
});

export type CreateInventoryUnitFormValues = z.infer<typeof createInventoryUnitSchema>;
