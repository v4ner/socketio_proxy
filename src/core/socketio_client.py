"""
Handles the Socket.IO client and its events.
"""
import socketio
import httpx
import json
from ..config.logging import logger

class SocketIOClient:
    """
    Manages a Socket.IO AsyncClient instance and its event handlers.
    """
    def __init__(self, callback_handler=None, headers=None):
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.http_client = httpx.AsyncClient()
        self.callback_handler = callback_handler if callback_handler else self._default_callback_handler
        self.headers = headers
        self.uri = None

        self._register_events()

    def _register_events(self):
        @self.sio.event
        async def connect():
            logger.info("Socket.IO client connected.")
            logger.info(f"Socket.IO client SID: {self.sio.sid}")

        @self.sio.event
        async def connect_error(data):
            logger.error(f"Socket.IO connection failed: {data}")

        @self.sio.event
        async def disconnect():
            logger.info("Socket.IO client disconnected.")

        @self.sio.on("*")
        async def catch_all(event, data):
            await self.callback_handler(event, data)

    async def _default_callback_handler(self, event, data):
        logger.warning(f"No custom callback handler provided. Received event: {event}, data: {data}")

    async def start(self, uri):
        self.uri = uri
        logger.info(f"sio start connect, uri={uri}, headers={self.headers}")
        await self.sio.connect(uri, headers=self.headers)

    async def stop(self):
        await self.sio.disconnect()

    async def restart(self):
        logger.info("Restarting Socket.IO connection...")
        if self.sio.connected:
            await self.sio.disconnect()
        
        if self.uri:
            try:
                await self.sio.connect(self.uri, headers=self.headers)
                logger.info("Socket.IO reconnected.")
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
        else:
            logger.warning("No URI available to restart connection.")

    @property
    def client(self):
        return self.sio

    @property
    def http_client_instance(self):
        return self.http_client