import { z } from "zod";
import { reportRangeOptions, reportTypeOptions } from "@/features/reports/constants/reportOptions";

export const createReportSchema = z.object({
  title: z.string().min(2, "Report title is required"),
  type: z.enum(reportTypeOptions.filter(option => option !== "All") as ["Sales", "Inventory", "Finance", "Operations"]),
  range: z.enum(reportRangeOptions),
  owner: z.string().min(2, "Owner is required")
});

export type CreateReportFormValues = z.infer<typeof createReportSchema>;
