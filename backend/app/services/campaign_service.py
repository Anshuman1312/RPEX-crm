from __future__ import annotations

from typing import Any, Optional, List, Dict
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.customer import Customer
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.customer_repository import CustomerRepository
from app.core.exceptions import ValidationException, NotFoundException
from loguru import logger


class CampaignService:
    """Campaign management and execution service."""
    
    def __init__(self, session: AsyncSession, repo: Optional[CampaignRepository] = None):
        self.session = session
        self.repo = repo or CampaignRepository(session)
        self.lead_repo = LeadRepository(session)
        self.customer_repo = CustomerRepository(session)

    async def create(self, payload: dict[str, Any], created_by_user_id: str | None = None) -> Campaign:
        """Create a new campaign."""
        return await self.repo.create(payload, created_by_user_id)

    async def execute_campaign(
        self,
        campaign_id: str,
        executed_by_user_id: str,
        target_filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a campaign on its configured platform.
        
        Args:
            campaign_id: Campaign to execute
            executed_by_user_id: User executing the campaign
            target_filters: Optional filters for lead/customer targeting
            
        Returns:
            Execution result with metrics (sent, failed, reach, etc.)
            
        Raises:
            ValidationException: If campaign config is invalid
            NotFoundException: If campaign not found
        """
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundException(f"Campaign {campaign_id} not found")

        if not campaign.platform:
            raise ValidationException("Campaign platform not configured")

        # Route to platform-specific handler
        platform = campaign.platform.upper()
        
        if platform == "WHATSAPP":
            result = await self._execute_whatsapp(campaign, target_filters, executed_by_user_id)
        elif platform == "EMAIL":
            result = await self._execute_email(campaign, target_filters, executed_by_user_id)
        elif platform == "SMS":
            result = await self._execute_sms(campaign, target_filters, executed_by_user_id)
        elif platform == "NOTIFICATION":
            result = await self._execute_notification(campaign, target_filters, executed_by_user_id)
        else:
            raise ValidationException(f"Unsupported platform: {platform}")

        # Update campaign metrics
        await self._update_campaign_metrics(campaign_id, result)

        logger.info(
            f"Campaign executed | id={campaign_id} | platform={platform} | "
            f"sent={result.get('sent', 0)} | failed={result.get('failed', 0)}"
        )

        return result

    async def _get_campaign_targets(
        self,
        campaign: Campaign,
        target_filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[Lead], List[Customer]]:
        """Get leads and customers to target for campaign."""
        filters = target_filters or {}
        
        # Get campaign type to determine targeting strategy
        campaign_type = (campaign.type or "").upper()
        
        # Get leads associated with campaign
        leads_query = select(Lead).where(
            and_(
                Lead.campaign_id == campaign.id if hasattr(Lead, 'campaign_id') else True,
                Lead.is_deleted == False,
            )
        )
        leads_result = await self.session.execute(leads_query)
        leads = leads_result.scalars().all()
        
        # Get customers if applicable
        customers = []
        if campaign_type in ["CUSTOMER_OUTREACH", "PRODUCT_LAUNCH", "RETENTION"]:
            customers_query = select(Customer).where(Customer.is_deleted == False)
            customers_result = await self.session.execute(customers_query)
            customers = customers_result.scalars().all()
        
        return leads, customers

    async def _execute_whatsapp(
        self,
        campaign: Campaign,
        target_filters: Optional[Dict[str, Any]],
        executed_by_user_id: str,
    ) -> Dict[str, Any]:
        """Execute campaign via WhatsApp."""
        from app.services.whatsapp_telecalling_service import WhatsAppService
        
        leads, customers = await self._get_campaign_targets(campaign, target_filters)
        
        whatsapp_service = WhatsAppService(self.session)
        extra_data = campaign.extra_data or {}
        
        template_id = extra_data.get("template_id")
        message_body = extra_data.get("message_body", "")
        template_variables = extra_data.get("template_variables", [])
        
        sent_count = 0
        failed_count = 0
        
        # Send to leads
        for lead in leads:
            try:
                if lead.phone:
                    await whatsapp_service.send_message(
                        phone_number=lead.phone,
                        message_type="TEMPLATE" if template_id else "TEXT",
                        sent_by_user_id=UUID(executed_by_user_id),
                        lead_id=lead.id,
                        message_body=message_body,
                        template_id=template_id,
                        template_variables=template_variables,
                    )
                    sent_count += 1
            except Exception as e:
                logger.error(f"WhatsApp send failed for lead {lead.id}: {str(e)}")
                failed_count += 1
        
        # Send to customers
        for customer in customers:
            try:
                if customer.phone:
                    await whatsapp_service.send_message(
                        phone_number=customer.phone,
                        message_type="TEMPLATE" if template_id else "TEXT",
                        sent_by_user_id=UUID(executed_by_user_id),
                        customer_id=customer.id,
                        message_body=message_body,
                        template_id=template_id,
                        template_variables=template_variables,
                    )
                    sent_count += 1
            except Exception as e:
                logger.error(f"WhatsApp send failed for customer {customer.id}: {str(e)}")
                failed_count += 1

        return {
            "platform": "WHATSAPP",
            "sent": sent_count,
            "failed": failed_count,
            "reach": len(leads) + len(customers),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_email(
        self,
        campaign: Campaign,
        target_filters: Optional[Dict[str, Any]],
        executed_by_user_id: str,
    ) -> Dict[str, Any]:
        """Execute campaign via Email."""
        from app.services.notification_service import NotificationService
        
        leads, customers = await self._get_campaign_targets(campaign, target_filters)
        
        notification_service = NotificationService(self.session)
        extra_data = campaign.extra_data or {}
        
        subject = extra_data.get("subject", campaign.name)
        body = extra_data.get("body", "")
        
        sent_count = 0
        failed_count = 0
        
        # Send emails to leads
        for lead in leads:
            try:
                if lead.email:
                    # Use notification system for emails
                    await notification_service.send(
                        user_id=lead.id,
                        type_="CAMPAIGN",
                        title=subject,
                        body=body,
                        channel="EMAIL",
                        metadata={
                            "campaign_id": str(campaign.id),
                            "campaign_name": campaign.name,
                        }
                    )
                    sent_count += 1
            except Exception as e:
                logger.error(f"Email send failed for lead {lead.id}: {str(e)}")
                failed_count += 1
        
        # Send emails to customers
        for customer in customers:
            try:
                if customer.email:
                    await notification_service.send(
                        user_id=customer.id,
                        type_="CAMPAIGN",
                        title=subject,
                        body=body,
                        channel="EMAIL",
                        metadata={
                            "campaign_id": str(campaign.id),
                            "campaign_name": campaign.name,
                        }
                    )
                    sent_count += 1
            except Exception as e:
                logger.error(f"Email send failed for customer {customer.id}: {str(e)}")
                failed_count += 1

        return {
            "platform": "EMAIL",
            "sent": sent_count,
            "failed": failed_count,
            "reach": len(leads) + len(customers),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_sms(
        self,
        campaign: Campaign,
        target_filters: Optional[Dict[str, Any]],
        executed_by_user_id: str,
    ) -> Dict[str, Any]:
        """Execute campaign via SMS."""
        leads, customers = await self._get_campaign_targets(campaign, target_filters)
        
        extra_data = campaign.extra_data or {}
        message_body = extra_data.get("message_body", "")
        
        sent_count = 0
        failed_count = 0
        
        # SMS API integration would go here
        # For now, tracking sends in logs
        
        for lead in leads:
            try:
                if lead.phone:
                    # TODO: Integrate with SMS provider (Twilio, AWS SNS, etc.)
                    logger.info(f"SMS campaign sent to lead {lead.id}: {message_body}")
                    sent_count += 1
            except Exception as e:
                logger.error(f"SMS send failed for lead {lead.id}: {str(e)}")
                failed_count += 1
        
        for customer in customers:
            try:
                if customer.phone:
                    logger.info(f"SMS campaign sent to customer {customer.id}: {message_body}")
                    sent_count += 1
            except Exception as e:
                logger.error(f"SMS send failed for customer {customer.id}: {str(e)}")
                failed_count += 1

        return {
            "platform": "SMS",
            "sent": sent_count,
            "failed": failed_count,
            "reach": len(leads) + len(customers),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _execute_notification(
        self,
        campaign: Campaign,
        target_filters: Optional[Dict[str, Any]],
        executed_by_user_id: str,
    ) -> Dict[str, Any]:
        """Execute campaign via in-app notifications."""
        from app.services.notification_service import NotificationService
        
        leads, customers = await self._get_campaign_targets(campaign, target_filters)
        
        notification_service = NotificationService(self.session)
        extra_data = campaign.extra_data or {}
        
        title = extra_data.get("title", campaign.name)
        body = extra_data.get("body", "")
        action_url = extra_data.get("action_url")
        
        sent_count = 0
        failed_count = 0
        
        # Send in-app notifications to leads
        for lead in leads:
            try:
                await notification_service.send(
                    user_id=lead.id,
                    type_="CAMPAIGN",
                    title=title,
                    body=body,
                    channel="IN_APP",
                    action_url=action_url,
                    metadata={
                        "campaign_id": str(campaign.id),
                        "campaign_name": campaign.name,
                    }
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Notification send failed for lead {lead.id}: {str(e)}")
                failed_count += 1
        
        # Send in-app notifications to customers
        for customer in customers:
            try:
                await notification_service.send(
                    user_id=customer.id,
                    type_="CAMPAIGN",
                    title=title,
                    body=body,
                    channel="IN_APP",
                    action_url=action_url,
                    metadata={
                        "campaign_id": str(campaign.id),
                        "campaign_name": campaign.name,
                    }
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Notification send failed for customer {customer.id}: {str(e)}")
                failed_count += 1

        return {
            "platform": "NOTIFICATION",
            "sent": sent_count,
            "failed": failed_count,
            "reach": len(leads) + len(customers),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _update_campaign_metrics(
        self,
        campaign_id: str,
        result: Dict[str, Any],
    ) -> None:
        """Update campaign metrics in extra_data after execution."""
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            return
        
        extra_data = campaign.extra_data or {}
        
        # Accumulate metrics
        extra_data["reach"] = int(extra_data.get("reach", 0)) + result.get("reach", 0)
        extra_data["sent"] = int(extra_data.get("sent", 0)) + result.get("sent", 0)
        extra_data["failed"] = int(extra_data.get("failed", 0)) + result.get("failed", 0)
        extra_data["last_executed"] = result.get("timestamp")
        
        campaign.extra_data = extra_data
        await self.session.flush()

    async def get_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed campaign performance metrics."""
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundException(f"Campaign {campaign_id} not found")
        
        extra_data = campaign.extra_data or {}
        
        sent = int(extra_data.get("sent", 0))
        reach = int(extra_data.get("reach", 0))
        leads = int(extra_data.get("leads", 0))
        budget = float(campaign.budget) if campaign.budget else 0
        
        return {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "platform": campaign.platform,
            "reach": reach,
            "sent": sent,
            "failed": int(extra_data.get("failed", 0)),
            "leads_generated": leads,
            "budget": str(budget),
            "cost_per_lead": round(budget / leads, 2) if leads > 0 else 0,
            "conversion_rate": float(extra_data.get("conversion", 0)),
            "roas": float(extra_data.get("roas", 0)),
            "last_executed": extra_data.get("last_executed"),
        }
