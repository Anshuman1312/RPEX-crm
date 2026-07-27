import { DashboardOverviewData, DashboardWidgetId } from "@/features/dashboard/types/dashboard";

export const dashboardOverviewMock: DashboardOverviewData = {
  kpis: [
    { id: "total-leads", label: "Total Leads", value: "2,431", change: "+12.4% vs last month", positive: true },
    { id: "total-open-leads", label: "Total Open Leads", value: "1,804", change: "+5.2% vs last week", positive: true },
    { id: "follow-leads", label: "Follow Leads", value: "328", change: "-12 overdue", positive: false },
    { id: "visit-scheduled", label: "Visit Scheduled", value: "92", change: "+15% this week", positive: true },
    { id: "total-visited-leads", label: "Total Visited Leads", value: "145", change: "+8% conversion", positive: true },
    { id: "total-booking-leads", label: "Total Booking Leads", value: "317", change: "+4.0% week-on-week", positive: true },
    { id: "total-lost-leads", label: "Total Future Perspective Leads", value: "102", change: "-2.1% decrease", positive: true },
    { id: "total-duplicate-leads", label: "Total Duplicate Leads", value: "43", change: "+1.5% increase", positive: false }
  ],
  leadTrend: [
    { name: "Jan", value: 220 },
    { name: "Feb", value: 270 },
    { name: "Mar", value: 255 },
    { name: "Apr", value: 320 },
    { name: "May", value: 360 },
    { name: "Jun", value: 410 }
  ],
  bookingPipeline: [
    { name: "New", value: 122 },
    { name: "Qualified", value: 88 },
    { name: "Proposal", value: 51 },
    { name: "Negotiation", value: 33 },
    { name: "Won", value: 23 }
  ],
  paymentBreakdown: [
    { label: "Paid", value: 74 },
    { label: "Partial", value: 18 },
    { label: "Overdue", value: 8 }
  ],
  tasks: [
    { label: "Due Today", count: 28, tone: "info" },
    { label: "Upcoming", count: 40, tone: "warning" },
    { label: "Overdue", count: 18, tone: "danger" },
    { label: "Completed", count: 56, tone: "success" }
  ],
  meetings: [
    { title: "Pricing Review - Zenith Towers", when: "Today 10:00 AM", owner: "Riya Shah" },
    { title: "Legal Handover - Orion Residency", when: "Today 12:30 PM", owner: "Karan Mehta" },
    { title: "Quarter Forecast Sync", when: "Today 4:00 PM", owner: "Aditi Jain" }
  ],
  recentActivity: [
    { id: "act-1", text: "Lead LD-1023 moved to Negotiation", timestamp: "5 minutes ago" },
    { id: "act-2", text: "Payment milestone updated for Project Aurelia", timestamp: "18 minutes ago" },
    { id: "act-3", text: "New booking created by Sales Team West", timestamp: "35 minutes ago" },
    { id: "act-4", text: "Task reassigned to CRM Executive queue", timestamp: "1 hour ago" }
  ],
  quickActions: [
    { id: "new-lead", label: "New Lead", description: "Create and assign a lead" },
    { id: "new-booking", label: "New Booking", description: "Start booking workflow" },
    { id: "new-payment", label: "Record Payment", description: "Capture customer payment" },
    { id: "schedule-meeting", label: "Schedule Meeting", description: "Create calendar event" }
  ]
};

export const defaultWidgetOrder: DashboardWidgetId[] = [
  "leadStats",
  "revenueTrend",
  "bookingPipeline",
  "payments",
  "tasks",
  "meetings",
  "recentActivity",
  "quickActions"
];
