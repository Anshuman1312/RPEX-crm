# RPEX Unified CRM - Production Blueprint

## 1) Objective
Build a production-grade unified CRM that extends the existing lead and campaign platform into a full business operating system across:
- Customer CRM
- Marketing CRM
- Telecalling CRM
- Sales Team CRM
- Finance
- Documents
- HR Module
- Vendor Module
- Reports
- WhatsApp CRM
- AI Assistant
- Automation Engine
- Role and Permission Management
- Integrations
- Channel Partner Portal (separate and isolated access)

## 2) Guiding Principles (Production First)
- Security-first: strict RBAC/ABAC, field-level restrictions, audit logs, PII encryption.
- Reliability: retries, idempotent jobs, queue-based async work, failure alerts.
- Observability: centralized logs, metrics, traces, SLA dashboards.
- Data quality: dedupe policies, ownership rules, approval workflows.
- Scale readiness: modular services, partition strategy, archival policies.
- Compliance readiness: GST artifacts, consent logs, document access trails.

## 3) Domain Modules and Key Entities

### 3.1 Customer CRM
Scope:
- Customer profile
- Personal details, family details, anniversaries, birthdays
- Documents and KYC
- Purchase history and payments
- Site visits
- Referrals
- Support tickets

Core entities:
- customer
- customer_family_member
- customer_document
- customer_purchase
- customer_payment
- customer_site_visit
- customer_referral
- customer_event (birthday/anniversary)
- support_ticket
- support_ticket_comment

### 3.2 Marketing CRM
Scope:
- Campaigns across Meta, Google, YouTube, SMS, Email, WhatsApp, Influencers
- Track budget, reach, leads, CPL, ROAS, conversion

Core entities:
- marketing_campaign
- campaign_channel
- campaign_spend
- campaign_lead_attribution
- campaign_performance_snapshot

### 3.3 Telecalling CRM
Scope:
- Daily call queue
- Connected, not connected, interested states
- Recordings, duration, daily targets, performance

Core entities:
- call_task
- call_log
- call_recording
- telecaller_target
- telecaller_daily_performance

### 3.4 Sales Team CRM
Scope:
- Sales executives, targets, sales, bookings, commissions
- Site visits, attendance, daily reports, leaderboards

Core entities:
- sales_target
- booking
- booking_installment
- commission_rule
- commission_ledger
- sales_site_visit
- attendance
- daily_sales_report
- leaderboard_snapshot

### 3.5 Finance
Scope:
- Customer payments
- Developer payments
- Marketing expenses
- Commissions
- Vendor payments
- Receipts, invoices, GST, profit reports

Core entities:
- finance_ledger_entry
- invoice
- receipt
- gst_document
- payout
- vendor_bill
- expense_head
- profit_snapshot

### 3.6 Documents
Scope:
- Store and classify Aadhaar, PAN, agreement, sale deed, NOCs, layout plans, brochures, videos, images

Core entities:
- document_asset
- document_category
- document_access_log
- document_version

### 3.7 HR Module
Scope:
- Employees, attendance, leave, salary, incentives, performance

Core entities:
- employee
- employee_attendance
- leave_request
- payroll_run
- incentive_ledger
- employee_performance_review

### 3.8 Vendor Module
Scope:
- Advertising agencies, printing, hoardings, influencers, photographers, videographers, architects, lawyers

Core entities:
- vendor
- vendor_category
- vendor_contract
- vendor_invoice
- vendor_performance

### 3.9 Reports
Scope:
- Daily/weekly/monthly reports
- Sales, lead, campaign, inventory, profit, employee reports

Core entities:
- report_definition
- report_execution
- report_schedule
- report_delivery_log

### 3.10 WhatsApp CRM
Scope:
- Click-to-chat
- Auto replies
- Templates
- Broadcast
- Campaign tracking
- Conversation history

Core entities:
- whatsapp_template
- whatsapp_conversation
- whatsapp_message
- whatsapp_broadcast
- whatsapp_automation_rule

### 3.11 AI Assistant
Scope:
- Natural language Q&A over CRM data
- Prediction and prioritization workflows

Core entities:
- ai_query_log
- ai_insight_snapshot
- lead_score
- sales_forecast

## 4) Automation Engine (Must-Have Workflows)
Event-driven workflows:
- Auto lead assignment
- Duplicate lead detection
- Missed follow-up alerts
- WhatsApp reminders
- Email automation
- Booking confirmation
- Invoice generation
- Payment reminders
- Anniversary/birthday wishes
- Daily performance reports
- Manager approval workflow
- Commission calculation
- AI lead scoring refresh

Design:
- Trigger source: API write, scheduler, webhook
- Rules: condition + action + channel + retry policy
- Execution: Celery queue + idempotency key
- Audit: immutable workflow execution log

## 5) Role and Permission Model
Roles requested:
- Super Admin (RPEX Management)
- Director
- Project Head
- Marketing Manager
- Sales Manager
- Sales Executive
- Telecaller
- CRM Executive
- Finance
- Legal
- HR
- Receptionist
- Channel Partner
- Developer (limited)
- Customer Portal User

Production permission model:
- Keep current permission-driven RBAC table structure.
- Add module-level and action-level permissions: view/create/update/delete/export/approve.
- Add record-level access filters by org, project, team, ownership.
- Add field masking for sensitive PII and financial data.

## 6) Channel Partner Separate Portal
Requirements:
- Separate frontend entrypoint and navigation profile.
- Access only to own leads, bookings, commissions, payouts, documents.
- No visibility into internal HR, full finance ledger, or unrelated customer records.

Technical implementation:
- Add partner-scoped tenant keys in domain records.
- Enforce partner filters in repository layer (server-side mandatory).
- Add dedicated APIs under /partner namespace.
- Add partner dashboard widgets: funnel, active leads, bookings, payable commissions, payout history.
- Add partner document center and ticketing.

## 7) Integration Map
Priority integrations:
- Meta Lead Ads
- Google Ads
- Google Analytics
- WhatsApp Business API
- SMTP/Gmail
- SMS gateway
- Google Maps
- Payment gateway (Razorpay/Cashfree)

Optional/future:
- DigiLocker/eSign
- Tally/Zoho Books

Integration design standards:
- Webhook signature validation
- Dead-letter queue for failed syncs
- Replay tools for operations team
- Unified integration log table

## 8) Suggested API Surface (Phase-Wise)
Add versioned routers:
- /api/v1/customers
- /api/v1/customer-payments
- /api/v1/telecalling
- /api/v1/sales
- /api/v1/finance
- /api/v1/documents
- /api/v1/hr
- /api/v1/vendors
- /api/v1/whatsapp
- /api/v1/automation
- /api/v1/ai
- /api/v1/partner

## 9) Data and Storage Architecture
Primary stores:
- PostgreSQL: transactional entities
- Redis: queues, caching, real-time counters
- Object storage (S3-compatible): documents, recordings, media

Recommended cross-cutting tables:
- audit_log (already present, extend usage)
- activity_stream
- notification
- approval_request
- integration_event_log

## 10) Non-Functional Production Requirements
- Auth: JWT with rotation + short-lived access tokens + secure refresh flow.
- Security: rate limits, brute-force protection, IP/device anomaly checks.
- Compliance: encryption at rest and in transit, PII access logs.
- Backups: PITR for PostgreSQL, daily object storage snapshot.
- DR: documented RTO/RPO and restore drill.
- Performance targets:
  - P95 API latency < 300ms for core read endpoints
  - Async import throughput > 10k records/hour
  - Report generation SLA per report type

## 11) Rollout Plan

### Phase 2 (8-10 weeks): Core Business Expansion
- Customer CRM
- Sales CRM basics (targets/bookings/commissions)
- Finance core (invoice/receipt/payment ledger)
- Document center
- Role expansion
- Channel Partner MVP

### Phase 3 (6-8 weeks): Marketing + Telecalling + WhatsApp
- Full campaign performance model
- Telecalling workflow with recordings
- WhatsApp templates and broadcast tracking
- Automation engine v1

### Phase 4 (6-8 weeks): HR + Vendor + AI + Advanced Reporting
- HR payroll/incentive workflow
- Vendor contracting and payouts
- AI assistant with governed query templates
- Forecasting and scoring models
- Executive dashboard pack

## 12) Immediate Implementation Tasks for This Repository
1. Extend permission seeds and role-permission mappings for all new modules.
2. Add Alembic migrations for customer, booking, finance, and documents as first expansion set.
3. Add backend routers/services/repositories for:
   - customers
   - sales
   - finance
   - documents
   - partner
4. Introduce object storage abstraction for documents and recordings.
5. Add frontend route groups and guarded pages for new roles.
6. Build separate partner layout and route tree.
7. Add workflow scheduler tasks for reminders, commissions, and daily reports.
8. Add integration_event_log and retry workers.

## 13) Success Metrics
- Lead-to-booking conversion uplift
- Follow-up SLA compliance
- Collection efficiency and overdue reduction
- Campaign ROAS by channel
- Telecaller connect-to-interest ratio
- Sales target attainment
- Partner satisfaction and payout turnaround time

## 14) Risks and Controls
- Scope overload risk: use phase gates and module exit criteria.
- Data leakage risk: enforce server-side row-level permission checks.
- Integration instability: retries + DLQ + replay console.
- Adoption risk: role-specific UX and training dashboards.
- Reporting drift: standard KPI dictionary and locked formulas.
