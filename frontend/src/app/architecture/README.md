# Step 2 - UI Architecture Blueprint

This document defines the enterprise UI architecture for the CRM shell.

## Architecture Layers

- app: Composition root, providers, global store, bootstrap effects.
- core: Cross-cutting platform capabilities (api, auth, theme, errors).
- layouts: Enterprise shell, sidebar, topbar, breadcrumbs, navigation contracts.
- routes: Route tree and route guards.
- features: Business modules with independent components/pages/services/store/types.
- components: Reusable primitives and domain-agnostic UI components.

## Shell Contracts

- Navigation is config-driven in `layouts/config/shell.config.ts`.
- Breadcrumbs are generated from active route path segments.
- Organization switcher state is persisted in global UI slice.
- Topbar hosts quick search, theme switch, notifications, and profile actions.
- Sidebar supports desktop collapse and mobile overlay patterns.

## State Boundaries

- UI state (theme, sidebar, active organization): Redux UI slice.
- Server state and caching: RTK Query.
- Session state: Auth slice.
- Route protection: Guard components + permission keys.

## Extension Rules

- Add modules by creating feature folder and a route entry.
- Add menu items only via shell config and permission mapping.
- Keep shell components stateless when possible; state lives in store.
- Keep data fetching out of layout shell unless globally required.

## Step 3 - Folder Structure Contract

Top-level frontend source structure:

- src/app
- src/core
- src/api
- src/services
- src/components
- src/layouts
- src/pages
- src/routes
- src/store
- src/hooks
- src/types
- src/utils
- src/constants
- src/config
- src/features

Every feature module follows this template:

- features/<module>/components
- features/<module>/pages
- features/<module>/hooks
- features/<module>/services
- features/<module>/types
- features/<module>/validation
- features/<module>/constants
- features/<module>/store

Scaffolded modules in this workspace:

- auth
- dashboard
- leads
- customers
- projects
- inventory
- bookings
- payments
- tasks
- meetings
- calendar
- notifications
- reports
- employees
- organization
- roles
- permissions
- settings
- profile
- activity-timeline
- workflow

## Step 4 - Routing Architecture Contract

Routing principles implemented:

- Guest and protected route trees are separated.
- Module pages are lazy loaded for code splitting.
- Protected module routes are generated from a central route catalog.
- Permission guards are enforced per module route.
- Route and navigation path literals are centralized in one constants file.

Key routing files:

- src/routes/config/paths.ts
- src/routes/config/moduleRoutes.tsx
- src/routes/components/RouteSuspense.tsx
- src/routes/guards/ProtectedRoute.tsx
- src/routes/guards/GuestRoute.tsx
- src/routes/router.tsx

Extension rules:

- Add a new module page route in src/routes/config/moduleRoutes.tsx.
- Use src/routes/config/paths.ts for all new path literals.
- Add route permission in src/config/permissions.ts.
- Add navigation item in src/layouts/config/shell.config.ts only when module is navigable.

## Step 5 - Layout Architecture Contract

Layout system implemented:

- Auth layout for guest pages (branding + security context + form slot).
- Enterprise layout for authenticated pages (sidebar, topbar, breadcrumbs, footer).
- Responsive sidebar with desktop collapse and mobile drawer overlay.
- Topbar interactions for theme switch, notifications panel, and profile menu.
- Shared footer and reusable page container primitives for module pages.

Key layout files:

- src/layouts/AuthLayout.tsx
- src/layouts/EnterpriseLayout.tsx
- src/layouts/components/SidebarNav.tsx
- src/layouts/components/TopBar.tsx
- src/layouts/components/AppBreadcrumbs.tsx
- src/layouts/components/AppFooter.tsx
- src/layouts/components/NotificationPanel.tsx
- src/layouts/components/ProfileMenu.tsx
- src/layouts/components/PageContainer.tsx

Extension rules:

- Keep global shell logic inside layouts, not inside feature pages.
- Keep module pages focused on domain content and compose with PageContainer.
- Add new global topbar actions as composable panels, not inline business logic.

## Step 6 - Authentication Architecture Contract

Authentication flow implemented:

- Login mutation with remember-me support.
- Auth payload persistence strategy:
	- local storage when remember-me is enabled.
	- session storage when remember-me is disabled.
- Store hydration from persisted auth payload on app bootstrap.
- Silent token refresh with refresh-token endpoint integration.
- Axios retry on 401 after refresh; session clear on unrecoverable refresh failure.
- Session-expired event broadcast and centralized store update handling.
- Guest/protected guards support bootstrap-pending state.
- Profile-menu sign out clears persisted auth and Redux auth state.

Key auth files:

- src/core/auth/tokenStorage.ts
- src/core/auth/authEvents.ts
- src/core/auth/authHttp.ts
- src/features/auth/store/authSlice.ts
- src/features/auth/services/authApi.ts
- src/features/auth/services/authLifecycle.ts
- src/features/auth/pages/LoginPage.tsx
- src/routes/guards/GuestRoute.tsx
- src/routes/guards/ProtectedRoute.tsx

Extension rules:

- Do not hardcode tokens in components.
- Route all refresh behavior through auth lifecycle service.
- Keep permission and role checks inside guards or dedicated gate components.

## Step 7 - Reusable Component System

Shared component domains implemented:

- ui: low-level primitives (button, input, card).
- forms: form field wrappers and search inputs.
- feedback: empty, loading, error, and skeleton states.
- data-display: KPI cards and status badges.
- charts: reusable chart wrappers.
- table: reusable TanStack table implementation with sorting, filtering, pagination, visibility toggle, and CSV export.

Key files:

- src/components/index.ts
- src/components/forms/*
- src/components/feedback/*
- src/components/data-display/*
- src/components/charts/*
- src/components/table/DataTable.tsx

Usage conventions:

- Import shared components from src/components/index.ts where possible.
- Keep module pages thin by composing PageContainer + reusable components.
- Avoid feature-specific behavior in shared components; extend via props and composition.

## Step 8 - Theme System Contract

Theme system implemented:

- Typed theme modes: light, dark, system.
- Resolved theme tracking for system preference fallback.
- Root-level theme metadata attributes:
	- data-theme-mode
	- data-theme-resolved
- Runtime synchronization with OS preference changes.
- Theme switcher component integrated into top navigation.
- Centralized theme preset metadata for brand configuration.

Key files:

- src/store/uiSlice.ts
- src/core/theme/useThemeSync.ts
- src/core/theme/theme.constants.ts
- src/core/theme/theme.config.ts
- src/layouts/components/ThemeModeSwitcher.tsx
- src/layouts/components/TopBar.tsx
- src/layouts/EnterpriseLayout.tsx
- src/styles/globals.css

Extension rules:

- Use uiSlice theme actions for mode changes.
- Avoid direct DOM theme mutations outside useThemeSync.
- Keep brand token changes in globals.css and theme.config.ts together.

## Step 10 - Lead Module Contract

Lead module implemented with feature-complete flow:

- Typed lead domain models and filter contracts.
- Zod-powered lead creation validation schema.
- RTK Query endpoints for lead list, create, and stage update workflows.
- Reusable lead feature components:
	- stats cards
	- search/filter bar
	- create lead form
	- table column factory with stage transition controls
- Leads page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/leads/types/lead.ts
- src/features/leads/validation/leadSchemas.ts
- src/features/leads/services/leadApi.ts
- src/features/leads/hooks/useLeadFilters.ts
- src/features/leads/components/*
- src/features/leads/pages/LeadsPage.tsx

Extension rules:

- Keep lead table behavior in reusable column builders.
- Prefer query filters over page-level ad hoc filtering when integrating real backend APIs.
- Keep lead form schema and API payload mapping aligned to avoid drift.

## Step 11 - Customer Module Contract

Customer module implemented with lifecycle-focused flow:

- Typed customer domain models for tiering, status, and account health.
- Zod-powered customer creation validation schema.
- RTK Query endpoints for customer list, create, and status update workflows.
- Reusable customer feature components:
	- stats cards
	- search/filter bar
	- create customer form
	- table column factory with inline status management
- Customers page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/customers/types/customer.ts
- src/features/customers/validation/customerSchemas.ts
- src/features/customers/services/customerApi.ts
- src/features/customers/hooks/useCustomerFilters.ts
- src/features/customers/components/*
- src/features/customers/pages/CustomersPage.tsx

Extension rules:

- Keep customer health semantics centralized in typed status enums.
- Keep customer segmentation controls reusable and independent of page layout.
- Keep customer create payload mapping aligned with validation schema.

## Step 12 - Project Module Contract

Project module implemented with delivery-focused flow:

- Typed project domain models for phase, health, and portfolio filtering.
- Zod-powered project creation validation schema.
- RTK Query endpoints for project list, create, and health update workflows.
- Reusable project feature components:
	- stats cards
	- search/filter bar
	- create project form
	- table column factory with inline health management
- Projects page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/projects/types/project.ts
- src/features/projects/validation/projectSchemas.ts
- src/features/projects/services/projectApi.ts
- src/features/projects/hooks/useProjectFilters.ts
- src/features/projects/components/*
- src/features/projects/pages/ProjectsPage.tsx

Extension rules:

- Keep project health semantics centralized in typed health enums.
- Keep project filter controls reusable and independent of page layout.
- Keep project create payload mapping aligned with validation schema.

## Step 13 - Inventory Module Contract

Inventory module implemented with stock-operations flow:

- Typed inventory domain models for category, status, and unit-level filtering.
- Zod-powered inventory unit creation validation schema.
- RTK Query endpoints for inventory list, create, and status update workflows.
- Reusable inventory feature components:
	- stats cards
	- search/filter bar
	- create inventory unit form
	- table column factory with inline status management
- Inventory page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/inventory/types/inventory.ts
- src/features/inventory/validation/inventorySchemas.ts
- src/features/inventory/services/inventoryApi.ts
- src/features/inventory/hooks/useInventoryFilters.ts
- src/features/inventory/components/*
- src/features/inventory/pages/InventoryPage.tsx

Extension rules:

- Keep inventory status semantics centralized in typed status enums.
- Keep inventory filter controls reusable and independent of page layout.
- Keep inventory unit create payload mapping aligned with validation schema.

## Step 14 - Booking Module Contract

Booking module implemented with pipeline-and-confirmation flow:

- Typed booking domain models for stage, payment state, and booking-level filtering.
- Zod-powered booking creation validation schema.
- RTK Query endpoints for booking list, create, and stage update workflows.
- Reusable booking feature components:
	- stats cards
	- search/filter bar
	- create booking form
	- table column factory with inline stage management
- Bookings page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/bookings/types/booking.ts
- src/features/bookings/validation/bookingSchemas.ts
- src/features/bookings/services/bookingApi.ts
- src/features/bookings/hooks/useBookingFilters.ts
- src/features/bookings/components/*
- src/features/bookings/pages/BookingsPage.tsx

Extension rules:

- Keep booking stage semantics centralized in typed stage enums.
- Keep booking filters reusable and independent of page layout.
- Keep booking create payload mapping aligned with validation schema.

## Step 15 - Payment Module Contract

Payment module implemented with reconciliation-focused flow:

- Typed payment domain models for method, status, and transaction-level filtering.
- Zod-powered payment creation validation schema.
- RTK Query endpoints for payment list, create, and status update workflows.
- Reusable payment feature components:
	- stats cards
	- search/filter bar
	- create payment form
	- table column factory with inline status management
- Payments page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/payments/types/payment.ts
- src/features/payments/validation/paymentSchemas.ts
- src/features/payments/services/paymentApi.ts
- src/features/payments/hooks/usePaymentFilters.ts
- src/features/payments/components/*
- src/features/payments/pages/PaymentsPage.tsx

Extension rules:

- Keep payment status semantics centralized in typed status enums.
- Keep payment filters reusable and independent of page layout.
- Keep payment create payload mapping aligned with validation schema.

## Step 16 - Task Module Contract

Task module implemented with execution-management flow:

- Typed task domain models for priority, status, and task-level filtering.
- Zod-powered task creation validation schema.
- RTK Query endpoints for task list, create, and status update workflows.
- Reusable task feature components:
	- stats cards
	- search/filter bar
	- create task form
	- table column factory with inline status management
- Tasks page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/tasks/types/task.ts
- src/features/tasks/validation/taskSchemas.ts
- src/features/tasks/services/taskApi.ts
- src/features/tasks/hooks/useTaskFilters.ts
- src/features/tasks/components/*
- src/features/tasks/pages/TasksPage.tsx

Extension rules:

- Keep task status semantics centralized in typed status enums.
- Keep task filters reusable and independent of page layout.
- Keep task create payload mapping aligned with validation schema.

## Step 17 - Meeting Module Contract

Meeting module implemented with scheduling-and-followup flow:

- Typed meeting domain models for type, status, and meeting-level filtering.
- Zod-powered meeting creation validation schema.
- RTK Query endpoints for meeting list, create, and status update workflows.
- Reusable meeting feature components:
	- stats cards
	- search/filter bar
	- create meeting form
	- table column factory with inline status management
- Meetings page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/meetings/types/meeting.ts
- src/features/meetings/validation/meetingSchemas.ts
- src/features/meetings/services/meetingApi.ts
- src/features/meetings/hooks/useMeetingFilters.ts
- src/features/meetings/components/*
- src/features/meetings/pages/MeetingsPage.tsx

Extension rules:

- Keep meeting status semantics centralized in typed status enums.
- Keep meeting filters reusable and independent of page layout.
- Keep meeting create payload mapping aligned with validation schema.

## Step 18 - Calendar Module Contract

Calendar module implemented with schedule-orchestration flow:

- Typed calendar event domain models for type, status, and event-level filtering.
- Zod-powered calendar event creation validation schema.
- RTK Query endpoints for calendar event list, create, and status update workflows.
- Reusable calendar feature components:
	- stats cards
	- search/filter bar
	- create calendar event form
	- table column factory with inline status management
- Calendar page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/calendar/types/calendar.ts
- src/features/calendar/validation/calendarSchemas.ts
- src/features/calendar/services/calendarApi.ts
- src/features/calendar/hooks/useCalendarFilters.ts
- src/features/calendar/components/*
- src/features/calendar/pages/CalendarPage.tsx

Extension rules:

- Keep calendar status semantics centralized in typed status enums.
- Keep calendar filters reusable and independent of page layout.
- Keep calendar event create payload mapping aligned with validation schema.

## Step 19 - Notification Module Contract

Notification module implemented with inbox-and-triage flow:

- Typed notification domain models for type, status, and notification-level filtering.
- Zod-powered notification creation validation schema.
- RTK Query endpoints for notification list, create, and status update workflows.
- Reusable notification feature components:
	- stats cards
	- search/filter bar
	- create notification form
	- table column factory with inline status management
- Notifications page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/notifications/types/notification.ts
- src/features/notifications/validation/notificationSchemas.ts
- src/features/notifications/services/notificationApi.ts
- src/features/notifications/hooks/useNotificationFilters.ts
- src/features/notifications/components/*
- src/features/notifications/pages/NotificationsPage.tsx

Extension rules:

- Keep notification status semantics centralized in typed status enums.
- Keep notification filters reusable and independent of page layout.
- Keep notification create payload mapping aligned with validation schema.

## Step 20 - Report Module Contract

Report module implemented with analytics-and-export flow:

- Typed report domain models for type, status, and run-level filtering.
- Zod-powered report creation validation schema.
- RTK Query endpoints for report list, create, and status update workflows.
- Reusable report feature components:
	- stats cards
	- search/filter bar
	- create report form
	- table column factory with inline status management
- Reports page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/reports/types/report.ts
- src/features/reports/validation/reportSchemas.ts
- src/features/reports/services/reportApi.ts
- src/features/reports/hooks/useReportFilters.ts
- src/features/reports/components/*
- src/features/reports/pages/ReportsPage.tsx

Extension rules:

- Keep report status semantics centralized in typed status enums.
- Keep report filters reusable and independent of page layout.
- Keep report create payload mapping aligned with validation schema.

## Step 21 - Employee Module Contract

Employee module implemented with workforce-operations flow:

- Typed employee domain models for department, status, and directory-level filtering.
- Zod-powered employee creation validation schema.
- RTK Query endpoints for employee list, create, and status update workflows.
- Reusable employee feature components:
	- stats cards
	- search/filter bar
	- create employee form
	- table column factory with inline status management
- Employees page composition with loading/error states, configurable filters, and create flow.

Key files:

- src/features/employees/types/employee.ts
- src/features/employees/validation/employeeSchemas.ts
- src/features/employees/services/employeeApi.ts
- src/features/employees/hooks/useEmployeeFilters.ts
- src/features/employees/components/*
- src/features/employees/pages/EmployeesPage.tsx

Extension rules:

- Keep employee status semantics centralized in typed status enums.
- Keep employee filters reusable and independent of page layout.
- Keep employee create payload mapping aligned with validation schema.

## Step 9 - Dashboard Module Contract

Dashboard capabilities implemented:

- KPI metrics cards.
- Lead trend chart.
- Booking pipeline chart.
- Payments distribution chart.
- Task summary widget.
- Meetings widget.
- Recent activity timeline widget.
- Quick actions widget.
- Per-widget visibility toggles with persisted preferences.

Key files:

- src/features/dashboard/types/dashboard.ts
- src/features/dashboard/constants/dashboardMockData.ts
- src/features/dashboard/services/dashboardService.ts
- src/features/dashboard/hooks/useDashboardOverview.ts
- src/features/dashboard/hooks/useDashboardPreferences.ts
- src/features/dashboard/components/*
- src/features/dashboard/pages/DashboardPage.tsx

Extension rules:

- Replace dashboardService mock implementation with RTK Query endpoint integration.
- Keep widget components independent and composition-driven.
- Add widget IDs to dashboard types and preferences hook before rendering new widgets.
