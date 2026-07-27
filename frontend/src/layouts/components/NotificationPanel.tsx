import { BellRing, CheckCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NotificationPanelProps {
  unreadCount: number;
}

const demoNotifications = [
  "Lead reassigned to Sales Team A",
  "Payment milestone reached for Project Orion",
  "Inventory threshold alert: Tower B units"
];

export function NotificationPanel({ unreadCount }: NotificationPanelProps) {
  return (
    <div className="w-80 rounded-lg border bg-card p-3 shadow-lg">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold">Notifications</p>
        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
          {unreadCount} unread
        </span>
      </div>

      <div className="space-y-2">
        {demoNotifications.map(notification => (
          <div key={notification} className="rounded-md border bg-background p-2 text-xs text-foreground">
            <div className="flex items-start gap-2">
              <BellRing className="mt-0.5 h-3.5 w-3.5 text-primary" />
              <span>{notification}</span>
            </div>
          </div>
        ))}
      </div>

      <Button className="mt-3 w-full" size="sm" variant="outline">
        <CheckCheck className="mr-2 h-4 w-4" />
        Mark all as read
      </Button>
    </div>
  );
}
