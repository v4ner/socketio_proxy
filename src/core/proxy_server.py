import asyncio
import uvicorn
from .socketio_client import SocketIOClient
from ..web.websocket_manager import WebSocketManager
from ..web import routes as api
from ..config.logging import logger
from ..config.settings import ProxyConfig
from ..handlers.event_handler_manager import EventHandlerManager

class SocketIOProxy:
    """
    A class to manage the lifecycle of the proxy server.
    """

    def __init__(self, proxy_config: ProxyConfig, event_handler_manager: EventHandlerManager):
        logger.info(f"SocketIOProxy __init__ called with:")
        logger.info(f"  socketio_server_url: {proxy_config.socketio_server_url}")
        logger.info(f"  listen_host: {proxy_config.listen_host}")
        logger.info(f"  listen_port: {proxy_config.listen_port}")
        logger.info(f"  base_url: {proxy_config.base_url}")
        logger.info(f"  headers: {proxy_config.headers}")

        self.proxy_config = proxy_config
        self.event_handler_manager = event_handler_manager
        self.websocket_manager = self.event_handler_manager.websocket_manager

        self.sio_client = SocketIOClient(
            callback_handler=self.event_handler_manager.handle, headers=self.proxy_config.headers
        )
        self.sio = self.sio_client.client
        self.http_client = self.sio_client.http_client_instance
        self.app = api.create_app(
            self.sio_client, self.proxy_config.base_url, self.websocket_manager
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

        logger.info(
            f"Proxy starting. HTTP interface listening on http://{self.proxy_config.listen_host}:{self.proxy_config.listen_port}"
        )

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
