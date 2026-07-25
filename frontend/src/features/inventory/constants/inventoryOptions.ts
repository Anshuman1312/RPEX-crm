import {
  InventoryCategory,
  InventoryStatus
} from "@/features/inventory/types/inventory";

export const inventoryCategoryOptions: Array<InventoryCategory | "All"> = [
  "All",
  "Apartment",
  "Villa",
  "Commercial",
  "Plot"
];

export const inventoryStatusOptions: Array<InventoryStatus | "All"> = [
  "All",
  "Available",
  "Reserved",
  "Sold"
];
