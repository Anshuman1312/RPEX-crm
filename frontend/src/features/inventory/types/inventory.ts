export type InventoryCategory = "Apartment" | "Villa" | "Commercial" | "Plot";
export type InventoryStatus = "Available" | "Reserved" | "Sold";

export interface InventoryUnitRecord {
  id: string;
  unitCode: string;
  project: string;
  category: InventoryCategory;
  status: InventoryStatus;
  sizeSqFt: number;
  price: number;
  assignedAgent: string;
  updatedAt: string;
}

export interface InventoryFilters {
  search?: string;
  category?: InventoryCategory | "All";
  status?: InventoryStatus | "All";
}

export interface InventoryStats {
  totalUnits: number;
  availableUnits: number;
  reservedUnits: number;
  soldUnits: number;
}

export interface InventoryListResponse {
  items: InventoryUnitRecord[];
  total: number;
  stats: InventoryStats;
}

export interface CreateInventoryUnitInput {
  unitCode: string;
  project: string;
  category: InventoryCategory;
  status: InventoryStatus;
  sizeSqFt: number;
  price: number;
  assignedAgent: string;
}
