import { CalendarClock, CheckSquare, Clock4, History, Zap } from "lucide-react";
import { Button, Card, CardContent, CardHeader, CardTitle, StatusBadge } from "@/components";
import {
  ActivityItem,
  MeetingSummary,
  QuickActionItem,
  TaskSummary
} from "@/features/dashboard/types/dashboard";

interface TaskSummaryCardProps {
  items: TaskSummary[];
}

export function TaskSummaryCard({ items }: TaskSummaryCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
        <CheckSquare className="h-4 w-4 text-primary" />
        <CardTitle className="text-sm font-semibold">Tasks Snapshot</CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0 space-y-2">
        {items.map(item => (
          <div className="flex items-center justify-between rounded-md border px-3 py-2" key={item.label}>
            <span className="text-sm">{item.label}</span>
            <StatusBadge label={String(item.count)} tone={item.tone} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

interface MeetingsCardProps {
  items: MeetingSummary[];
}

export function MeetingsCard({ items }: MeetingsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
        <CalendarClock className="h-4 w-4 text-primary" />
        <CardTitle className="text-sm font-semibold">Upcoming Meetings</CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0 space-y-3">
        {items.map(item => (
          <div className="rounded-md border p-3" key={`${item.title}-${item.when}`}>
            <p className="text-sm font-medium">{item.title}</p>
            <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
              <Clock4 className="h-3.5 w-3.5" />
              <span>{item.when}</span>
              <span>• {item.owner}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

interface RecentActivityCardProps {
  items: ActivityItem[];
}

export function RecentActivityCard({ items }: RecentActivityCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
        <History className="h-4 w-4 text-primary" />
        <CardTitle className="text-sm font-semibold">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0 space-y-2">
        {items.map(item => (
          <div className="rounded-md border p-3" key={item.id}>
            <p className="text-sm">{item.text}</p>
            <p className="mt-1 text-xs text-muted-foreground">{item.timestamp}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

interface QuickActionsCardProps {
  items: QuickActionItem[];
  onActionClick: (item: QuickActionItem) => void;
}

export function QuickActionsCard({ items, onActionClick }: QuickActionsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2 space-y-0 p-4 pb-3">
        <Zap className="h-4 w-4 text-primary" />
        <CardTitle className="text-sm font-semibold">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0 grid gap-2">
        {items.map(item => (
          <Button
            className="h-auto items-start justify-start px-3 py-2 text-left"
            key={item.id}
            onClick={() => onActionClick(item)}
            variant="outline"
          >
            <div>
              <p className="text-sm font-medium">{item.label}</p>
              <p className="text-xs text-muted-foreground">{item.description}</p>
            </div>
          </Button>
        ))}
      </CardContent>
    </Card>
  );
}
