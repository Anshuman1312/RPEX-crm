from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionNames:
    MANAGE_USERS: str = "manage_users"
    MANAGE_WEBSITES: str = "manage_websites"
    VIEW_LEADS: str = "view_leads"
    EDIT_LEADS: str = "edit_leads"
    MANAGE_FOLLOWUPS: str = "manage_followups"
    VIEW_ANALYTICS: str = "view_analytics"
    EXPORT_REPORTS: str = "export_reports"
    SCHEDULE_REPORTS: str = "schedule_reports"
    MANAGE_CAMPAIGNS: str = "manage_campaigns"
    MANAGE_KEYWORDS: str = "manage_keywords"
    MANAGE_CUSTOMERS: str = "manage_customers"
    MANAGE_SALES: str = "manage_sales"
    MANAGE_FINANCE: str = "manage_finance"
    MANAGE_DOCUMENTS: str = "manage_documents"
    ACCESS_PARTNER_PORTAL: str = "access_partner_portal"


PERMISSIONS = PermissionNames()
