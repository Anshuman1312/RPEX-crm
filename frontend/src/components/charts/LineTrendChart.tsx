import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components";

interface LineTrendDatum {
  name: string;
  value: number;
}

interface LineTrendChartProps {
  data: LineTrendDatum[];
  title: string;
}

export function LineTrendChart({ data, title }: LineTrendChartProps) {
  return (
    <Card>
      <CardHeader className="p-4 pb-3">
        <CardTitle className="text-sm font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
              <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
              <Tooltip />
              <Line dataKey="value" stroke="hsl(var(--primary))" strokeWidth={2} type="monotone" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
