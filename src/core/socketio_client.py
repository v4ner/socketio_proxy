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
            logger.info(f"sio cli connected, sid={self.sio.sid}")

        @self.sio.event
        async def connect_error(data):
            logger.error(f"sio conn failed, data={data}")

        @self.sio.event
        async def disconnect():
            logger.info("sio cli disconnected.")

        @self.sio.on("*")
        async def catch_all(event, data):
            await self.callback_handler(event, data)

    async def _default_callback_handler(self, event, data):
        logger.warning(f"No custom handler. Evt: {event}, Data: {data}")

    async def start(self, uri):
        self.uri = uri
        logger.info(f"sio connect to {uri}, headers={self.headers}")
        await self.sio.connect(uri, headers=self.headers)

    async def stop(self):
        await self.sio.disconnect()

    async def restart(self):
        logger.info("sio restarting...")
        if self.sio.connected:
            await self.sio.disconnect()
        
        if self.uri:
            try:
                await self.sio.connect(self.uri, headers=self.headers)
                logger.info("sio reconnected.")
            except Exception as e:
                logger.error(f"sio reconnect failed: {e}")
        else:
            logger.warning("sio restart failed: no URI.")

    @property
    def client(self):
        return self.sio

    @property
    def http_client_instance(self):
        return self.http_client