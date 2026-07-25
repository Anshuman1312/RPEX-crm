import {
  CreateInventoryUnitInput,
  InventoryListResponse,
  InventoryStats,
  InventoryUnitRecord
} from "@/features/inventory/types/inventory";

function formatDate(offset: number) {
  const date = new Date();
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialInventoryUnitRecords: InventoryUnitRecord[] = [
  {
    id: "IU-4101",
    unitCode: "A-1204",
    project: "Skyline Heights Phase 2",
    category: "Apartment",
    status: "Available",
    sizeSqFt: 1480,
    price: 13800000,
    assignedAgent: "Neha",
    updatedAt: formatDate(-1)
  },
  {
    id: "IU-4102",
    unitCode: "V-08",
    project: "Orchid Greens",
    category: "Villa",
    status: "Reserved",
    sizeSqFt: 2650,
    price: 28200000,
    assignedAgent: "Aman",
    updatedAt: formatDate(-3)
  },
  {
    id: "IU-4103",
    unitCode: "C-302",
    project: "Emerald Business Park",
    category: "Commercial",
    status: "Available",
    sizeSqFt: 980,
    price: 9200000,
    assignedAgent: "Riya",
    updatedAt: formatDate(-2)
  },
  {
    id: "IU-4104",
    unitCode: "P-19",
    project: "Riverfront Residency",
    category: "Plot",
    status: "Sold",
    sizeSqFt: 1800,
    price: 11100000,
    assignedAgent: "Rohan",
    updatedAt: formatDate(-5)
  }
];

export function buildInventoryStats(records: InventoryUnitRecord[]): InventoryStats {
  return {
    totalUnits: records.length,
    availableUnits: records.filter(record => record.status === "Available").length,
    reservedUnits: records.filter(record => record.status === "Reserved").length,
    soldUnits: records.filter(record => record.status === "Sold").length
  };
}

export function buildInventoryListResponse(records: InventoryUnitRecord[]): InventoryListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildInventoryStats(records)
  };
}

export function createInventoryUnitRecord(
  payload: CreateInventoryUnitInput,
  index: number
): InventoryUnitRecord {
  return {
    id: `IU-${4100 + index}`,
    unitCode: payload.unitCode,
    project: payload.project,
    category: payload.category,
    status: payload.status,
    sizeSqFt: payload.sizeSqFt,
    price: payload.price,
    assignedAgent: payload.assignedAgent,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
