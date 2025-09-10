from fastapi import APIRouter, Request, Depends
from src.config.logging import logger
from src.core.socketio_client import SocketIOClient
from src.web.dependencies import app_context

router = APIRouter()

@router.post("/custom_api/echo")
async def custom_echo(request: Request):
    """一个自定义的 echo API 端点。"""
    body = await request.json()
    logger.info(f"Custom API '/custom_api/echo' called with body: {body}")
    return {"status": "ok", "echo": body}

@router.get("/custom_api/health")
async def custom_health():
    """一个自定义的健康检查端点。"""
    return {"status": "ok", "message": "Custom API is healthy"}

@router.post("/custom_api/send_sio_message")
async def send_sio_message(
    request: Request,
    sio_client: SocketIOClient = Depends(lambda: app_context.get_sio_client())
):
    """
    一个通过注入的 sio_client 向 Socket.IO 服务器发送消息的端点。
    """
    if not sio_client.client.connected:
        return {"status": "error", "message": "Socket.IO client is not connected."}
    
    body = await request.json()
    event = body.get("event", "message")
    data = body.get("data", {})
    
    await sio_client.client.emit(event, data)
    logger.info(f"Sent SIO message via custom API. Event: {event}, Data: {data}")
    
    return {"status": "ok", "message": "SIO message sent."}