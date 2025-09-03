"""
Defines the FastAPI application and its routes.
"""
from fastapi import FastAPI, Request, HTTPException, APIRouter, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import json
from src.config.logging import logger
from typing import List

from src.core.socketio_client import SocketIOClient
 
def create_app(sio_client: SocketIOClient, base_url: str = "", websocket_manager=None, external_routers: List[APIRouter] = None):
    app = FastAPI()
    router = APIRouter(prefix=base_url)

    templates = Jinja2Templates(directory="src/web_client/templates")
    app.mount(base_url + "/static", StaticFiles(directory="src/web_client/static"), name="static")

    @router.get("/")
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request, "base_url": base_url})

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket_manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except Exception as e:
            logger.error(f"WS disconnected: {e}")
        finally:
            websocket_manager.disconnect(websocket)

    @router.post("/send_message")
    async def send_message(request: Request):
        """
        Receives a message via HTTP POST and emits it to the Socket.IO server.
        """
        if not sio_client.client.connected:
            raise HTTPException(status_code=503, detail="Socket.IO client is not connected.")

        try:
            body = await request.json()
            event = body["event"]
            data = body["data"]
        except (KeyError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid request format. Required JSON: {'event': str, 'data': dict}")

        await sio_client.client.emit(event, data)
        return {"status": "ok"}

    @router.post("/restart_sio")
    async def restart_sio_connection():
        """
        Restarts the Socket.IO client connection.
        """
        logger.info("Restart SIO conn request.")
        await sio_client.restart()
        return {"status": "ok", "message": "Socket.IO connection restarted."}

    @router.post("/test")
    async def test_endpoint(request: Request):
        """
        A test endpoint that logs the request body and returns a status.
        """
        body = await request.json()
        logger.info(f"Test request. Body: {body}")
        return {"status": "ok", "message": "Request logged"}

    app.include_router(router)

    # register extend routers
    if external_routers:
        for external_router in external_routers:
            app.include_router(external_router, prefix=base_url)

    return app