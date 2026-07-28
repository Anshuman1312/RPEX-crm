# Import all models here so Alembic's autogenerate can detect them.
# Add each import as the corresponding model file is implemented.

from app.models.user import (
    User,
    Department,
    Designation,
    Role,
    Permission,
    RolePermission,
    UserPermission,
    UserSession,
    LoginHistory,
)
from app.models.lead import Lead, LeadActivity, LeadAssignment
from app.models.customer import Customer, CustomerAddress, CustomerKYC, CustomerPreference
from app.models.project import Project, Block, Building, Floor, Unit, UnitAvailabilityLog, ProjectAmenity
from app.models.booking import Booking, BookingPaymentPlan, BookingApproval, BookingCancellation, Possession
from app.models.invoice import Invoice, InvoiceItem, FinanceLedgerEntry, InvoicePaymentMapping
from app.models.followup import FollowUp, FollowUpTask, FollowUpOutcome, FollowUpAttachment
from app.models.task import Task, TaskChecklist, TaskComment, TaskAttachment, Activity
from app.models.notification import Notification, NotificationPreference, NotificationTemplate
from app.models.setting import AppSetting, UserSetting
from app.models.audit_log import AuditLog
from app.models.whatsapp_telecalling import (
    WhatsAppTemplate, WhatsAppInteraction, TelecallingScript, TelecallingCall
)
# from app.models.inventory import Unit, UnitType, UnitAvailabilityLog
# from app.models.booking import Booking, BookingApproval, BookingCancellation, Possession
# from app.models.payment import PaymentPlan, PaymentSchedule, Payment, PaymentLedger
# from app.models.followup import Followup, SiteVisit
# from app.models.meeting import Meeting, MeetingParticipant
# from app.models.task import Task, TaskComment
# from app.models.notification import Notification, NotificationTemplate, NotificationLog
# from app.models.audit import AuditLog
from app.models.system import SystemSetting
from app.models.campaign import Campaign
from app.models.seo_keyword import SEOKeyword
from app.models.customer_payment import CustomerPayment
from app.models.document import DocumentAsset
from app.models.hr import HREmployee, HRRecord
from app.models.inventory import InventoryUnit
from app.models.website import Website
from app.models.vendor import Vendor
from app.models.sales import SalesBooking
from app.models.sales_team import SalesTeamReport
from app.models.site_visit import SiteVisit
