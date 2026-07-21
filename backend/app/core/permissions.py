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
    MANAGE_PROJECTS: str = "manage_projects"
    MANAGE_KEYWORDS: str = "manage_keywords"
    MANAGE_CUSTOMERS: str = "manage_customers"
    MANAGE_SALES: str = "manage_sales"
    MANAGE_FINANCE: str = "manage_finance"
    MANAGE_DOCUMENTS: str = "manage_documents"
    MANAGE_HR: str = "manage_hr"
    MANAGE_VENDORS: str = "manage_vendors"
    MANAGE_WHATSAPP: str = "manage_whatsapp"
    MANAGE_TELECALLING: str = "manage_telecalling"
    MANAGE_SALES_TEAM: str = "manage_sales_team"
    ACCESS_PARTNER_PORTAL: str = "access_partner_portal"
    VIEW_OWN_BOOKINGS_PAYMENTS: str = "view_own_bookings_payments"
    VIEW_INVENTORY: str = "view_inventory"
    MANAGE_INVENTORY: str = "manage_inventory"
    VIEW_CUSTOMERS: str = "view_customers"
    MANAGE_CUSTOMERS: str = "manage_customers"
    VIEW_SALES: str = "view_sales"
    MANAGE_BOOKINGS: str = "manage_bookings"
    MANAGE_FINANCE: str = "manage_finance"
    MANAGE_HR: str = "manage_hr"
    MANAGE_VENDORS: str = "manage_vendors"
    MANAGE_SITE_VISITS: str = "manage_site_visits"
    VIEW_TELECALLING: str = "view_telecalling"
    MANAGE_TASKS: str = "manage_tasks"
    
    # Portal Access
    VIEW_CUSTOMER_PORTAL: str = "view_customer_portal"


PERMISSIONS = PermissionNames()
