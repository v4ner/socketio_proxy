import asyncio
import uvicorn
from .socketio_client import SocketIOClient
from src.web.websocket_manager import WebSocketManager
from src.web import routes as api
from src.config.logging import logger
from src.config.settings import ProxyConfig
from src.handlers.event_handler_manager import EventHandlerManager
from typing import List
from fastapi import APIRouter

class SocketIOProxy:
    """
    A class to manage the lifecycle of the proxy server.
    """

    def __init__(self, proxy_config: ProxyConfig, event_handler_manager: EventHandlerManager, sio_client: SocketIOClient, external_routers: List[APIRouter] = None):
        logger.info(f"Proxy init. SIO URL: {proxy_config.socketio_server_url}, Listen: {proxy_config.listen_host}:{proxy_config.listen_port}, Base URL: {proxy_config.base_url}, Headers: {proxy_config.headers}")

        self.proxy_config = proxy_config
        self.event_handler_manager = event_handler_manager
        self.websocket_manager = self.event_handler_manager.websocket_manager
        self.sio_client = sio_client
        self.sio = self.sio_client.client
        self.http_client = self.sio_client.http_client_instance
        self.external_routers = external_routers if external_routers else []
        self.app = api.create_app(
            self.sio_client, self.proxy_config.base_url, self.websocket_manager, self.external_routers
        )

        self.server = None
        self.sio_task = None
        self.server_task = None

    async def start(self):
        """
        Starts the proxy server and the Socket.IO client.
        """
        server_config = uvicorn.Config(
            self.app, host=self.proxy_config.listen_host, port=self.proxy_config.listen_port, log_level="warning"
        )
        self.server = uvicorn.Server(server_config)

        logger.info(f"Proxy starting. HTTP listening on http://{self.proxy_config.listen_host}:{self.proxy_config.listen_port}")

        self.sio_task = asyncio.create_task(
            self.sio_client.start(self.proxy_config.socketio_server_url)
        )
        self.server_task = asyncio.create_task(self.server.serve())

        await asyncio.gather(self.sio_task, self.server_task)

    async def stop(self):
        """
        Stops the proxy server and disconnects the Socket.IO client.
        """
        if self.sio_task and not self.sio_task.done():
            self.sio_task.cancel()
        if self.sio.connected:
            await self.sio.disconnect()

        if self.server and self.server.started:
            self.server.should_exit = True
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()

        await self.http_client.aclose()
        logger.info("Proxy stopped.")
