import { LucideIcon, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/utils/cn";

interface KpiCardProps {
  title: string;
  value: string;
  change?: string;
  positive?: boolean;
  icon?: LucideIcon;
}

export function KpiCard({ title, value, change, positive = true, icon: Icon = TrendingUp }: KpiCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <CardTitle className="text-sm text-muted-foreground">{title}</CardTitle>
        <div className="grid h-8 w-8 place-items-center rounded-md bg-primary/10 text-primary">
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent className="space-y-1">
        <p className="text-2xl font-semibold">{value}</p>
        {change ? (
          <p className={cn("text-xs", positive ? "text-emerald-600" : "text-destructive")}>{change}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}
