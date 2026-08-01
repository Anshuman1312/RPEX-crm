from enum import Enum


# ── Identity & Access ────────────────────────────────────────────────────────

class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class DeviceType(str, Enum):
    """Device type for session tracking."""

    WEB = "web"
    MOBILE = "mobile"
    TABLET = "tablet"
    API = "api"


class LoginStatus(str, Enum):
    """Login attempt outcome."""

    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


# ── Lead Management ──────────────────────────────────────────────────────────

class LeadSource(str, Enum):
    """Lead acquisition source."""

    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    GOOGLE_ADS = "google_ads"
    WEBSITE = "website"
    WHATSAPP = "whatsapp"
    WALK_IN = "walk_in"
    REFERRAL = "referral"
    CHANNEL_PARTNER = "channel_partner"
    CLIENT_REFERENCE = "client_reference"
    EXHIBITION_EVENT = "exhibition_event"
    JUSTDIAL = "justdial"
    LINKEDIN = "linkedin"
    99_ACRES = "99_acres"
    ONLINE_PORTAL = "online_portal"
    PHONE = "phone"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    ADVERTISEMENT = "advertisement"
    PROPERTY_PORTAL = "property_portal"
    AGENT = "agent"
    OTHER = "other"


class LeadStatus(str, Enum):
    """Lead lifecycle status."""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"
    INACTIVE = "inactive"


class LeadPriority(str, Enum):
    """Lead priority level."""

    HOT = "hot"  # 🔥
    WARM = "warm"  # 🟡
    COLD = "cold"  # 🔵
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LeadLostReason(str, Enum):
    """Reason lead was marked lost."""

    BUDGET = "budget"
    TIMING = "timing"
    LOCATION = "location"
    PRODUCT = "product"
    COMPETITOR = "competitor"
    NO_RESPONSE = "no_response"
    CHANGED_MIND = "changed_mind"
    OTHER = "other"


class LeadPurpose(str, Enum):
    """Lead's purpose for property acquisition."""

    INVESTMENT = "investment"
    SELF_USE = "self_use"
    BUSINESS = "business"


class PropertyType(str, Enum):
    """Property type classification."""

    PLOT = "plot"
    VILLA = "villa"
    FLAT = "flat"
    COMMERCIAL = "commercial"
    OTHER = "other"


class TimeDuration(str, Enum):
    """Timeline for property purchase."""

    IMMEDIATE = "immediate"
    THREE_TO_SIX_MONTHS = "3_6_months"
    SIX_TO_TWELVE_MONTHS = "6_12_months"
    ONE_PLUS_YEAR = "1_plus_year"


# ── Customer Management ──────────────────────────────────────────────────────

class CustomerStatus(str, Enum):
    """Customer account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


class CustomerType(str, Enum):
    """Customer classification."""

    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    PARTNERSHIP = "partnership"
    TRUST = "trust"
    NRI = "nri"


class KYCStatus(str, Enum):
    """Know-Your-Customer verification status."""

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ── Projects & Inventory ─────────────────────────────────────────────────────

class ProjectStatus(str, Enum):
    """Project lifecycle status."""

    PLANNING = "planning"
    APPROVED = "approved"
    LAUNCHED = "launched"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, Enum):
    """Project classification."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    PLOTTED = "plotted"


class UnitType(str, Enum):
    """Unit classification."""

    STUDIO = "studio"
    ONE_BHK = "1bhk"
    TWO_BHK = "2bhk"
    THREE_BHK = "3bhk"
    FOUR_BHK = "4bhk"
    PENTHOUSE = "penthouse"
    COMMERCIAL = "commercial"
    OFFICE = "office"


class UnitStatus(str, Enum):
    """Unit availability status."""

    AVAILABLE = "available"
    BLOCKED = "blocked"
    BOOKED = "booked"
    SOLD = "sold"
    UNSOLD = "unsold"


# ── Bookings & Payments ──────────────────────────────────────────────────────

class BookingStatus(str, Enum):
    """Booking lifecycle status."""

    INITIATED = "initiated"
    CONFIRMED = "confirmed"
    APPROVED = "approved"
    AGREEMENT_SIGNED = "agreement_signed"
    POSSESSION = "possession"
    CANCELLED = "cancelled"
    DEFAULTED = "defaulted"


class BookingApprovalStatus(str, Enum):
    """Booking approval workflow status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVERTED = "reverted"


class PaymentStatus(str, Enum):
    """Payment status."""

    PENDING = "pending"
    OVERDUE = "overdue"
    PAID = "paid"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class PaymentMethod(str, Enum):
    """Payment method."""

    CASH = "cash"
    CHEQUE = "cheque"
    DEMAND_DRAFT = "demand_draft"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    NEFT = "neft"
    RTGS = "rtgs"
    OTHER = "other"


# ── Follow-ups & Communication ───────────────────────────────────────────────

class FollowUpStatus(str, Enum):
    """Follow-up lifecycle status."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class FollowUpType(str, Enum):
    """Follow-up activity type."""

    CALL = "call"
    EMAIL = "email"
    SMS = "sms"
    MEETING = "meeting"
    SITE_VISIT = "site_visit"
    VIDEO_CALL = "video_call"
    WHATSAPP = "whatsapp"
    OTHER = "other"


class FollowUpMode(str, Enum):
    """Follow-up mode/channel of communication."""

    CALL = "call"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    MEETING = "meeting"
    SMS = "sms"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    OTHER = "other"


class FollowUpTaskType(str, Enum):
    """Follow-up task type."""

    CALL = "call"
    EMAIL = "email"
    SMS = "sms"
    MEETING = "meeting"
    SITE_VISIT = "site_visit"
    PROPOSAL = "proposal"
    DOCUMENT = "document"
    FOLLOW_UP = "follow_up"


class FollowUpTaskStatus(str, Enum):
    """Follow-up task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class FollowUpOutcomeType(str, Enum):
    """Follow-up outcome classification."""

    MOVED_FORWARD = "moved_forward"
    STALLED = "stalled"
    CONVERTED = "converted"
    LOST = "lost"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"


class FollowupType(str, Enum):
    """Follow-up activity type (legacy)."""

    PHONE_CALL = "phone_call"
    EMAIL = "email"
    SMS = "sms"
    IN_PERSON = "in_person"
    VIDEO_CALL = "video_call"
    WHATSAPP = "whatsapp"
    SITE_VISIT = "site_visit"


class SiteVisitStatus(str, Enum):
    """Site visit status."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class MeetingStatus(str, Enum):
    """Meeting status."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class TaskStatus(str, Enum):
    """Task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    OVERDUE = "overdue"


class TaskPriority(str, Enum):
    """Task priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Notifications ───────────────────────────────────────────────────────────

class NotificationType(str, Enum):
    """Notification type/category."""

    LEAD_UPDATE = "lead_update"
    BOOKING_UPDATE = "booking_update"
    PAYMENT_REMINDER = "payment_reminder"
    PAYMENT_RECEIVED = "payment_received"
    TASK_ASSIGNED = "task_assigned"
    MEETING_REMINDER = "meeting_reminder"
    SITE_VISIT_REMINDER = "site_visit_reminder"
    SYSTEM_ALERT = "system_alert"
    DOCUMENT_UPLOADED = "document_uploaded"
    APPROVAL_REQUIRED = "approval_required"


class NotificationChannel(str, Enum):
    """Notification delivery channel."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"


# ── Approval Workflow ────────────────────────────────────────────────────────

class ApprovalStatus(str, Enum):
    """Approval request status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVERTED = "reverted"
    ESCALATED = "escalated"


class ApprovalLevel(str, Enum):
    """Approval hierarchy level."""

    JUNIOR = "junior"
    SENIOR = "senior"
    MANAGER = "manager"
    DIRECTOR = "director"
    CEO = "ceo"


# ── Financial ────────────────────────────────────────────────────────────────

class LedgerEntryType(str, Enum):
    """Ledger transaction type."""

    CREDIT = "credit"
    DEBIT = "debit"


class TransactionCategory(str, Enum):
    """Financial transaction category."""

    BOOKING = "booking"
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    REVERSAL = "reversal"
    REVERSAL_BOOKING = "reversal_booking"


# ── Document Management ──────────────────────────────────────────────────────

class DocumentType(str, Enum):
    """Document classification."""

    AGREEMENT = "agreement"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    BANK_STATEMENT = "bank_statement"
    ID_PROOF = "id_proof"
    ADDRESS_PROOF = "address_proof"
    INCOME_PROOF = "income_proof"
    PROPERTY_DOCUMENT = "property_document"
    APPROVAL_LETTER = "approval_letter"
    SURVEY_REPORT = "survey_report"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document workflow status."""

    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ── Telecalling ──────────────────────────────────────────────────────────────

class CallStatus(str, Enum):
    """Telecall status."""

    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    COMPLETED = "completed"
    MISSED = "missed"
    BUSY = "busy"
    FAILED = "failed"


class CallDirection(str, Enum):
    """Telecall direction."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallOutcome(str, Enum):
    """Telecall outcome."""

    SUCCESSFUL = "successful"
    NOT_INTERESTED = "not_interested"
    CALLBACK_SCHEDULED = "callback_scheduled"
    NO_RESPONSE = "no_response"
    INVALID_NUMBER = "invalid_number"
    DO_NOT_CALL = "do_not_call"
