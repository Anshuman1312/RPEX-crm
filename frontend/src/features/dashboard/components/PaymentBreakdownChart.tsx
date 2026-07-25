import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components";
import { PaymentBreakdown } from "@/features/dashboard/types/dashboard";

interface PaymentBreakdownChartProps {
  data: PaymentBreakdown[];
}

const COLORS = ["hsl(var(--primary))", "#f59e0b", "#ef4444"];

export function PaymentBreakdownChart({ data }: PaymentBreakdownChartProps) {
  return (
    <Card>
      <CardHeader className="p-4 pb-3">
        <CardTitle className="text-sm font-semibold">Payments Distribution</CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <div className="h-64">
          <ResponsiveContainer>
            <PieChart>
              <Pie data={data} dataKey="value" innerRadius={55} nameKey="label" outerRadius={85}>
                {data.map((entry, index) => (
                  <Cell fill={COLORS[index % COLORS.length]} key={`${entry.label}-${index}`} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {data.map((entry, index) => (
            <div className="inline-flex items-center gap-2 text-xs text-muted-foreground" key={entry.label}>
              <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: COLORS[index % COLORS.length] }} />
              {entry.label}: {entry.value}%
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
