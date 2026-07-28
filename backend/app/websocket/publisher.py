from __future__ import annotations

import json
from typing import Any

from app.core.redis import redis_client

LEAD_CHANNEL = "analytics:leads"


async def publish_event(channel: str, payload: dict[str, Any]) -> int:
    """Publish JSON payload to a Redis pubsub channel."""
    return await redis_client.publish(channel, json.dumps(payload, default=str))


async def publish_lead_event(payload: dict[str, Any]) -> int:
    """Convenience publisher for lead analytics updates."""
    return await publish_event(LEAD_CHANNEL, payload)
