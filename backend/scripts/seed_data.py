#!/usr/bin/env python3
"""
Seed script for RPEX CRM — creates initial users, roles, app settings,
whatsapp templates, call scripts, and sample data for development.

Usage:
    cd backend
    python scripts/seed_data.py
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import hash_password


# ── Engine ────────────────────────────────────────────────────────────

engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def seed(session: AsyncSession) -> None:
    from sqlalchemy import text

    # Ensure numbering sequences exist
    await session.execute(text("""
        INSERT INTO system_settings (id, key, int_value)
        VALUES
            (gen_random_uuid(), 'seq.LEAD', 0),
            (gen_random_uuid(), 'seq.CUST', 0),
            (gen_random_uuid(), 'seq.PROJ', 0),
            (gen_random_uuid(), 'seq.BOOK', 0),
            (gen_random_uuid(), 'seq.INV',  0),
            (gen_random_uuid(), 'seq.FOLUP', 0),
            (gen_random_uuid(), 'seq.TASK', 0)
        ON CONFLICT (key) DO NOTHING;
    """))

    # ── Superadmin user ───────────────────────────────────────────────
    admin_id = str(uuid.uuid4())
    sales_mgr_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    await session.execute(text("""
        INSERT INTO users (id, email, full_name, hashed_password, role, is_active, is_superuser, is_verified)
        VALUES
            (:id1, 'admin@rpex.com', 'System Admin', :pw, 'superadmin', true, true, true),
            (:id2, 'salesmanager@rpex.com', 'Sales Manager', :pw, 'sales_manager', true, false, true),
            (:id3, 'agent@rpex.com', 'Sales Agent', :pw, 'sales_agent', true, false, true)
        ON CONFLICT (email) DO NOTHING;
    """), {
        "id1": admin_id,
        "id2": sales_mgr_id,
        "id3": agent_id,
        "pw": hash_password("Admin@123"),
    })

    # ── App settings ──────────────────────────────────────────────────
    settings_data = [
        ("crm.company_name",        "Company Name",          "general",  "string", "RPEX Realty Pvt Ltd", False, False),
        ("crm.support_email",       "Support Email",         "general",  "string", "support@rpex.com",    False, False),
        ("crm.support_phone",       "Support Phone",         "general",  "string", "+91-9999999999",      False, False),
        ("crm.currency",            "Currency",              "general",  "string", "INR",                 False, True),
        ("crm.gst_number",          "GST Number",            "general",  "string", "",                    False, False),
        ("crm.rera_number",         "RERA Number",           "general",  "string", "",                    False, False),
        ("jwt.access_token_expire", "Access Token TTL (min)","security", "int",    None,                  False, True),
        ("jwt.refresh_token_days",  "Refresh Token TTL (d)", "security", "int",    None,                  False, True),
        ("email.from_name",         "Email From Name",       "email",    "string", "RPEX CRM",            False, False),
        ("email.from_address",      "Email From Address",    "email",    "string", "noreply@rpex.com",    False, False),
        ("whatsapp.api_url",        "WhatsApp API URL",      "whatsapp", "string", "",                    False, False),
        ("whatsapp.api_key",        "WhatsApp API Key",      "whatsapp", "string", "",                    True,  False),
        ("booking.max_hold_days",   "Booking Hold Days",     "booking",  "int",    None,                  False, False),
    ]

    for key, label, cat, dtype, val, sensitive, readonly in settings_data:
        sid = str(uuid.uuid4())
        val_col = "value_string" if dtype == "string" else "value_int"
        val_expr = f"'{val}'" if val and dtype == "string" else ("7" if dtype == "int" else "NULL")
        await session.execute(text(f"""
            INSERT INTO app_settings (id, key, label, category, data_type, {val_col}, is_sensitive, is_readonly)
            VALUES ('{sid}', '{key}', '{label}', '{cat}', '{dtype}', {val_expr}, {str(sensitive).lower()}, {str(readonly).lower()})
            ON CONFLICT (key) DO NOTHING;
        """))

    # ── WhatsApp templates ────────────────────────────────────────────
    wa_templates = [
        (
            "lead_welcome",
            "UTILITY",
            "Welcome to {{1}}! Thank you for your interest. Our team will contact you shortly.",
            None,
            "en",
        ),
        (
            "site_visit_confirmation",
            "UTILITY",
            "Your site visit for *{{1}}* is confirmed on *{{2}}* at *{{3}}*. We look forward to seeing you!",
            None,
            "en",
        ),
        (
            "payment_reminder",
            "UTILITY",
            "Reminder: Your payment of ₹{{1}} for booking {{2}} is due on {{3}}. Please make the payment to avoid late charges.",
            None,
            "en",
        ),
        (
            "booking_confirmed",
            "UTILITY",
            "Congratulations! 🎉 Your booking {{1}} for {{2}} has been confirmed. Welcome to the RPEX family!",
            None,
            "en",
        ),
        (
            "invoice_sent",
            "UTILITY",
            "Invoice {{1}} for ₹{{2}} has been sent to your email {{3}}. Due date: {{4}}.",
            None,
            "en",
        ),
    ]
    for name, category, body, footer, lang in wa_templates:
        wid = str(uuid.uuid4())
        footer_sql = f"'{footer}'" if footer else "NULL"
        await session.execute(text(f"""
            INSERT INTO whatsapp_templates (id, name, language, category, body_text, footer_text, status, is_active)
            VALUES ('{wid}', '{name}', '{lang}', '{category}', '{body}', {footer_sql}, 'APPROVED', true)
            ON CONFLICT (name) DO NOTHING;
        """))

    # ── Telecalling scripts ───────────────────────────────────────────
    scripts = [
        (
            "cold_call_intro",
            "COLD_CALL",
            "Good [morning/afternoon], am I speaking with {{lead_name}}? This is {{agent_name}} calling from RPEX Realty.",
            """I'm calling because we have some exciting new properties that might match what you're looking for.
We specialize in residential and commercial real estate in [city].

Do you have a couple of minutes to discuss your requirements?""",
            {
                "Not interested": "I completely understand. Could I just share some information about our upcoming projects? No obligation at all.",
                "Already have an agent": "That's great! I'm just sharing information about our latest developments. You can always compare options.",
                "Busy right now": "Of course! When would be a good time to call back?",
            },
            "Thank you for your time, {{lead_name}}. I'll send you our project brochure on WhatsApp. Have a great day!",
        ),
        (
            "followup_call",
            "FOLLOWUP",
            "Hello {{lead_name}}, this is {{agent_name}} from RPEX Realty. We spoke earlier about your property requirements.",
            """I wanted to follow up and check if you had a chance to review the information I sent you.
Do you have any questions about the projects we discussed?""",
            {
                "Price too high": "We understand budget is important. We do have flexible payment plans including construction-linked and down-payment schemes. Shall I walk you through those?",
                "Need more time": "Absolutely, take your time. Should I schedule a call next week?",
                "Comparing options": "That makes sense. What are your key criteria? Let me help you compare more effectively.",
            },
            "Great talking to you again! I'll send you the updated brochure and price list. Looking forward to our next conversation.",
        ),
        (
            "site_visit_invite",
            "QUALIFICATION",
            "Hi {{lead_name}}, I'm {{agent_name}} from RPEX. I have an exciting update about the project you were enquiring about.",
            """We're conducting exclusive site visits this weekend for interested buyers.
This would give you a chance to see the property, meet the team, and understand the investment potential.

Would you be available on Saturday or Sunday for a quick 30-minute visit?""",
            {
                "Too far": "We provide complimentary pickup for our site visits. Would that make it more convenient?",
                "Not ready to buy": "No pressure at all! The visit is just to help you visualize the project better. Many buyers tell us it helped them decide.",
                "Weekend not free": "No problem! We can also arrange weekday visits. What time works for you?",
            },
            "Excellent! I'll send you a confirmation on WhatsApp with all the details. See you soon!",
        ),
    ]
    for name, purpose, intro, main, objections, closing in scripts:
        scid = str(uuid.uuid4())
        import json
        obj_json = json.dumps(objections).replace("'", "''")
        intro_esc = intro.replace("'", "''")
        main_esc = main.replace("'", "''")
        closing_esc = closing.replace("'", "''")
        await session.execute(text(f"""
            INSERT INTO telecalling_scripts (id, name, purpose, intro_text, main_script, objections, closing_text, is_active, created_by_user_id)
            VALUES ('{scid}', '{name}', '{purpose}', '{intro_esc}', '{main_esc}', '{obj_json}', '{closing_esc}', true, '{admin_id}')
            ON CONFLICT (name) DO NOTHING;
        """))

    # ── Notification templates ────────────────────────────────────────
    notif_templates = [
        ("lead_assigned", "LEAD_UPDATE", "in_app", "New Lead Assigned: {{ lead_number }}", "Lead {{ lead_name }} has been assigned to you.", ["lead_number", "lead_name"]),
        ("task_assigned", "TASK_ASSIGNED", "in_app", "New Task: {{ task_title }}", "You have been assigned a new task: {{ task_title }}. Due: {{ due_date }}", ["task_title", "due_date"]),
        ("payment_due", "PAYMENT_REMINDER", "email", "Payment Due: {{ booking_number }}", "Payment of ₹{{ amount }} for booking {{ booking_number }} is due on {{ due_date }}.", ["booking_number", "amount", "due_date"]),
        ("booking_approved", "BOOKING_UPDATE", "in_app", "Booking Approved: {{ booking_number }}", "Booking {{ booking_number }} has been approved and moved to the next stage.", ["booking_number"]),
    ]
    for name, ntype, channel, title_t, body_t, variables in notif_templates:
        ntid = str(uuid.uuid4())
        var_json = json.dumps(variables).replace("'", "''")
        title_esc = title_t.replace("'", "''")
        body_esc = body_t.replace("'", "''")
        await session.execute(text(f"""
            INSERT INTO notification_templates (id, name, notification_type, channel, title_template, body_template, variables, is_active)
            VALUES ('{ntid}', '{name}', '{ntype}', '{channel}', '{title_esc}', '{body_esc}', '{var_json}', true)
            ON CONFLICT (name) DO NOTHING;
        """))

    await session.commit()
    print("✓ Seed data inserted successfully!")
    print(f"  Admin: admin@rpex.com / Admin@123")
    print(f"  Sales Manager: salesmanager@rpex.com / Admin@123")
    print(f"  Agent: agent@rpex.com / Admin@123")


async def main() -> None:
    async with SessionLocal() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
