"""
Common utilities for the CRM application.

Exports:
  - Numbering: Sequential number generation (LEAD-000001, etc.)
  - Filters: Filter parameter models for all domain entities
  - Query: QueryBuilder, FullTextSearchBuilder, AggregationBuilder
  - Validators: DateValidator, AmountValidator, TextValidator, etc.
  - Enums: All domain enums (UserStatus, LeadStatus, etc.)
  - Converters: Type conversion helpers
  - Pagination: Pagination parameters and utilities
  - Response: API response envelopes
"""

from app.utils.numbering import NumberingService, NumberingPrefix
from app.utils.filters import (
    SortDirection,
    DateRangeFilter,
    StatusFilter,
    TextSearchFilter,
    SortBy,
    LeadFilterParams,
    CustomerFilterParams,
    ProjectFilterParams,
    BookingFilterParams,
    PaymentFilterParams,
    TaskFilterParams,
    NotificationFilterParams,
)
from app.utils.query import QueryBuilder, FullTextSearchBuilder, AggregationBuilder
from app.utils.validators import (
    DateValidator,
    AmountValidator,
    ContactValidator,
    TextValidator,
    StateValidator,
    RangeValidator,
)
from app.utils.enums import (
    UserStatus,
    DeviceType,
    LoginStatus,
    LeadSource,
    LeadStatus,
    LeadPriority,
    LeadLostReason,
    CustomerStatus,
    CustomerType,
    KYCStatus,
    ProjectStatus,
    ProjectType,
    UnitType,
    UnitStatus,
    BookingStatus,
    BookingApprovalStatus,
    PaymentStatus,
    PaymentMethod,
    FollowupType,
    SiteVisitStatus,
    MeetingStatus,
    TaskStatus,
    TaskPriority,
    NotificationType,
    NotificationChannel,
    ApprovalStatus,
    ApprovalLevel,
    LedgerEntryType,
    TransactionCategory,
    DocumentType,
    DocumentStatus,
    CallStatus,
    CallDirection,
    CallOutcome,
)
from app.utils.converters import (
    TypeConverter,
    DateTimeConverter,
    CurrencyConverter,
    EnumConverter,
    DictConverter,
    PhoneConverter,
)
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import APIResponse, PaginatedResponse, ok, created, error

__all__ = [
    # Numbering
    "NumberingService",
    "NumberingPrefix",
    # Filters
    "SortDirection",
    "DateRangeFilter",
    "StatusFilter",
    "TextSearchFilter",
    "SortBy",
    "LeadFilterParams",
    "CustomerFilterParams",
    "ProjectFilterParams",
    "BookingFilterParams",
    "PaymentFilterParams",
    "TaskFilterParams",
    "NotificationFilterParams",
    # Query
    "QueryBuilder",
    "FullTextSearchBuilder",
    "AggregationBuilder",
    # Validators
    "DateValidator",
    "AmountValidator",
    "ContactValidator",
    "TextValidator",
    "StateValidator",
    "RangeValidator",
    # Enums
    "UserStatus",
    "DeviceType",
    "LoginStatus",
    "LeadSource",
    "LeadStatus",
    "LeadPriority",
    "LeadLostReason",
    "CustomerStatus",
    "CustomerType",
    "KYCStatus",
    "ProjectStatus",
    "ProjectType",
    "UnitType",
    "UnitStatus",
    "BookingStatus",
    "BookingApprovalStatus",
    "PaymentStatus",
    "PaymentMethod",
    "FollowupType",
    "SiteVisitStatus",
    "MeetingStatus",
    "TaskStatus",
    "TaskPriority",
    "NotificationType",
    "NotificationChannel",
    "ApprovalStatus",
    "ApprovalLevel",
    "LedgerEntryType",
    "TransactionCategory",
    "DocumentType",
    "DocumentStatus",
    "CallStatus",
    "CallDirection",
    "CallOutcome",
    # Converters
    "TypeConverter",
    "DateTimeConverter",
    "CurrencyConverter",
    "EnumConverter",
    "DictConverter",
    "PhoneConverter",
    # Pagination
    "PaginationParams",
    "get_pagination_params",
    # Response
    "APIResponse",
    "PaginatedResponse",
    "ok",
    "created",
    "error",
]
