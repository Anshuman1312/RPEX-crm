from fastapi import APIRouter

# ── Module routers are registered here as each step is implemented ─────────────
# Uncomment and add imports as modules are built in subsequent steps.

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.leads import router as leads_router
from app.api.v1.customers import router as customers_router
from app.api.v1.projects import router as projects_router
from app.api.v1.bookings import router as bookings_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.followups import router as followups_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.reports import router as reports_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.audit import router as audit_router
from app.api.v1.communications import router as communications_router
# from app.api.v1.inventory import router as inventory_router
# from app.api.v1.bookings import router as bookings_router
# from app.api.v1.payments import router as payments_router
# from app.api.v1.followups import router as followups_router
# from app.api.v1.meetings import router as meetings_router
# from app.api.v1.tasks import router as tasks_router
# from app.api.v1.notifications import router as notifications_router
# from app.api.v1.dashboard import router as dashboard_router
# from app.api.v1.reports import router as reports_router
# from app.api.v1.settings import router as settings_router

api_router = APIRouter()

api_router.include_router(auth_router,          prefix="/auth",          tags=["Authentication"])
api_router.include_router(users_router,         prefix="/users",         tags=["Users"])
api_router.include_router(leads_router,         prefix="/leads",         tags=["Leads"])
api_router.include_router(customers_router,     prefix="/customers",     tags=["Customers"])
api_router.include_router(projects_router,      prefix="/projects",      tags=["Projects"])
api_router.include_router(bookings_router,      prefix="/bookings",      tags=["Bookings"])
api_router.include_router(invoices_router,      prefix="/invoices",      tags=["Invoices"])
api_router.include_router(followups_router,     prefix="/followups",     tags=["Follow-ups"])
api_router.include_router(tasks_router,         prefix="/tasks",         tags=["Tasks"])
api_router.include_router(reports_router,       prefix="/reports",       tags=["Reports"])
api_router.include_router(notifications_router, prefix="/notifications",  tags=["Notifications"])
api_router.include_router(dashboard_router,      prefix="/dashboard",     tags=["Dashboard"])
api_router.include_router(audit_router,          prefix="/audit",         tags=["Audit"])
api_router.include_router(communications_router, prefix="",               tags=["Communications"])
# api_router.include_router(customers_router,     prefix="/customers",     tags=["Customers"])
# api_router.include_router(projects_router,      prefix="/projects",      tags=["Projects"])
# api_router.include_router(inventory_router,     prefix="/inventory",     tags=["Inventory"])
# api_router.include_router(bookings_router,      prefix="/bookings",      tags=["Bookings"])
# api_router.include_router(payments_router,      prefix="/payments",      tags=["Payments"])
# api_router.include_router(followups_router,     prefix="/followups",     tags=["Follow-ups"])
# api_router.include_router(meetings_router,      prefix="/meetings",      tags=["Meetings"])
# api_router.include_router(tasks_router,         prefix="/tasks",         tags=["Tasks"])
# api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
# api_router.include_router(dashboard_router,     prefix="/dashboard",     tags=["Dashboard"])
# api_router.include_router(reports_router,       prefix="/reports",       tags=["Reports"])
# api_router.include_router(settings_router,      prefix="/settings",      tags=["Settings"])
