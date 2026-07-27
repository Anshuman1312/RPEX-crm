"""
FastAPI routes for WhatsApp messaging and Telecalling.

WhatsApp:
  POST   /whatsapp/send                  — send outbound message
  POST   /whatsapp/webhook               — inbound message / status webhook
  POST   /whatsapp/status-update         — delivery status update from provider
  GET    /whatsapp/messages              — list interactions (filterable)
  GET    /whatsapp/messages/{id}         — single interaction
  GET    /whatsapp/stats                 — delivery statistics
  GET    /whatsapp/templates             — list templates
  POST   /whatsapp/templates             — create template

Telecalling:
  POST   /telecalling/calls              — log new call
  GET    /telecalling/calls              — list calls (filterable)
  GET    /telecalling/calls/{id}         — single call
  PATCH  /telecalling/calls/{id}         — update call outcome
  GET    /telecalling/stats              — call statistics
  GET    /telecalling/scripts            — list scripts
  POST   /telecalling/scripts            — create script
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.whatsapp_telecalling import (
    WhatsAppSendRequest, WhatsAppInteractionResponse, WhatsAppWebhookPayload,
    WhatsAppStatusUpdate, WhatsAppStats, WhatsAppTemplateCreate, WhatsAppTemplateResponse,
    TelecallingCallCreate, TelecallingCallUpdate, TelecallingCallResponse,
    TelecallingScriptCreate, TelecallingScriptResponse, TelecallingStats,
)
from app.services.whatsapp_telecalling_service import WhatsAppService, TelecallingService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse

router = APIRouter()


# ══════════════════════════════════════════════════════
# WHATSAPP
# ══════════════════════════════════════════════════════

@router.post("/whatsapp/send", status_code=status.HTTP_201_CREATED, response_model=dict)
async def send_whatsapp(
    request: WhatsAppSendRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("whatsapp.send")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Send an outbound WhatsApp message (TEXT or TEMPLATE)."""
    svc = WhatsAppService(session)
    interaction = await svc.send_message(
        phone_number=request.phone_number,
        message_type=request.message_type,
        sent_by_user_id=current_user.id,
        lead_id=request.lead_id,
        customer_id=request.customer_id,
        message_body=request.message_body,
        template_id=request.template_id,
        template_variables=request.template_variables,
        media_url=request.media_url,
    )
    await session.commit()
    return created(
        data=WhatsAppInteractionResponse.model_validate(interaction).__dict__,
        message="Message queued for delivery.",
    )


@router.post("/whatsapp/webhook", status_code=status.HTTP_200_OK, response_model=dict)
async def whatsapp_webhook(
    payload: WhatsAppWebhookPayload,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Receive inbound WhatsApp message from provider webhook (no auth required)."""
    svc = WhatsAppService(session)
    interaction = await svc.handle_webhook(payload.model_dump())
    await session.commit()
    return ok(data={"id": str(interaction.id)})


@router.post("/whatsapp/status-update", status_code=status.HTTP_200_OK, response_model=dict)
async def whatsapp_status_update(
    payload: WhatsAppStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update delivery/read status from provider (no auth required)."""
    svc = WhatsAppService(session)
    interaction = await svc.update_delivery_status(
        external_message_id=payload.external_message_id,
        status=payload.status,
        timestamp=payload.timestamp,
        error_message=payload.error_message,
    )
    await session.commit()
    return ok(data={"id": str(interaction.id), "status": interaction.status})


@router.get("/whatsapp/messages", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_whatsapp_messages(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("whatsapp.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    lead_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    phone_number: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List WhatsApp interactions with filtering."""
    svc = WhatsAppService(session)
    interactions, total = await svc.list_interactions(
        lead_id=UUID(lead_id) if lead_id else None,
        customer_id=UUID(customer_id) if customer_id else None,
        direction=direction,
        status=status_filter,
        phone_number=phone_number,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    data = [WhatsAppInteractionResponse.model_validate(i).__dict__ for i in interactions]
    return PaginatedResponse.build(data=data, total=total, page=pagination.page, page_size=pagination.page_size).__dict__


@router.get("/whatsapp/stats", status_code=status.HTTP_200_OK, response_model=dict)
async def get_whatsapp_stats(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("whatsapp.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get WhatsApp delivery statistics."""
    svc = WhatsAppService(session)
    return ok(data=await svc.get_stats())


@router.get("/whatsapp/templates", status_code=status.HTTP_200_OK, response_model=dict)
async def list_whatsapp_templates(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("whatsapp.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List WhatsApp message templates."""
    svc = WhatsAppService(session)
    templates = await svc.list_templates(active_only=active_only)
    data = [WhatsAppTemplateResponse.model_validate(t).__dict__ for t in templates]
    return ok(data=data)


@router.post("/whatsapp/templates", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_whatsapp_template(
    request: WhatsAppTemplateCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("whatsapp.manage_templates")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create a new WhatsApp message template."""
    svc = WhatsAppService(session)
    template = await svc.create_template(**request.model_dump())
    await session.commit()
    return created(
        data=WhatsAppTemplateResponse.model_validate(template).__dict__,
        message="Template created successfully.",
    )


# ══════════════════════════════════════════════════════
# TELECALLING
# ══════════════════════════════════════════════════════

@router.post("/telecalling/calls", status_code=status.HTTP_201_CREATED, response_model=dict)
async def log_call(
    request: TelecallingCallCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Log a new telecalling call."""
    svc = TelecallingService(session)
    call = await svc.log_call(
        phone_number=request.phone_number,
        direction=request.direction,
        agent_user_id=current_user.id,
        lead_id=request.lead_id,
        customer_id=request.customer_id,
        script_id=request.script_id,
        notes=request.notes,
    )
    await session.commit()
    return created(
        data=TelecallingCallResponse.model_validate(call).__dict__,
        message="Call logged successfully.",
    )


@router.get("/telecalling/calls", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_calls(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    agent_id: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    call_status: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None),
    followup_required: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List telecalling calls with filtering."""
    svc = TelecallingService(session)
    calls, total = await svc.list_calls(
        agent_id=UUID(agent_id) if agent_id else None,
        lead_id=UUID(lead_id) if lead_id else None,
        customer_id=UUID(customer_id) if customer_id else None,
        direction=direction,
        call_status=call_status,
        outcome=outcome,
        followup_required=followup_required,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    data = [TelecallingCallResponse.model_validate(c).__dict__ for c in calls]
    return PaginatedResponse.build(data=data, total=total, page=pagination.page, page_size=pagination.page_size).__dict__


@router.get("/telecalling/calls/{call_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_call(
    call_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get a single telecalling call."""
    svc = TelecallingService(session)
    call = await svc.get_call(UUID(call_id))
    return ok(data=TelecallingCallResponse.model_validate(call).__dict__)


@router.patch("/telecalling/calls/{call_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_call(
    call_id: str,
    request: TelecallingCallUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update call outcome, status, duration and notes."""
    svc = TelecallingService(session)
    call = await svc.update_call(UUID(call_id), **request.model_dump(exclude_unset=True))
    await session.commit()
    return ok(data=TelecallingCallResponse.model_validate(call).__dict__)


@router.get("/telecalling/stats", status_code=status.HTTP_200_OK, response_model=dict)
async def get_telecalling_stats(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get telecalling statistics."""
    svc = TelecallingService(session)
    return ok(data=await svc.get_stats())


@router.get("/telecalling/scripts", status_code=status.HTTP_200_OK, response_model=dict)
async def list_scripts(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List active call scripts."""
    svc = TelecallingService(session)
    scripts = await svc.list_scripts()
    data = [TelecallingScriptResponse.model_validate(s).__dict__ for s in scripts]
    return ok(data=data)


@router.post("/telecalling/scripts", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_script(
    request: TelecallingScriptCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("telecalling.manage_scripts")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create a telecalling script."""
    svc = TelecallingService(session)
    script = await svc.create_script(
        created_by_user_id=current_user.id,
        **request.model_dump(),
    )
    await session.commit()
    return created(
        data=TelecallingScriptResponse.model_validate(script).__dict__,
        message="Script created successfully.",
    )
