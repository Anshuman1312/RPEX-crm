import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import redis_client
from app.websocket.connection_manager import manager
from app.websocket.publisher import LEAD_CHANNEL

router = APIRouter()


@router.websocket("/ws/analytics")
async def analytics_ws(websocket: WebSocket):
    await manager.connect(websocket)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(LEAD_CHANNEL)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await websocket.send_text(data)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        await pubsub.unsubscribe(LEAD_CHANNEL)
        await pubsub.aclose()
