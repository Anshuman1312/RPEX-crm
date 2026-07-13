import json

from app.core.redis import redis_client

LEAD_CHANNEL = "leads:events"


async def publish_lead_event(payload: dict):
    await redis_client.publish(LEAD_CHANNEL, json.dumps(payload))
