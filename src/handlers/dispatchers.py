import aiofiles
import httpx
from ..web.websocket_manager import WebSocketManager
from ..config.logging import logger
from abc import ABC, abstractmethod
import json

class Dispatcher(ABC):
    @abstractmethod
    async def dispatch(self, message: dict):
        pass

class FileDispatcher(Dispatcher):
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def dispatch(self, message: dict):
        async with aiofiles.open(self.file_path, mode='a') as f:
            await f.write(json.dumps(message) + '\n')

class HttpDispatcher(Dispatcher):
    def __init__(self, callback_url: str, http_client: httpx.AsyncClient):
        self.callback_url = callback_url
        self.http_client = http_client

    async def dispatch(self, message: dict):
        try:
            await self.http_client.post(self.callback_url, json=message)
        except httpx.RequestError as e:
            logger.error(f"Error forwarding event to callback URL: {e}")

class WebSocketDispatcher(Dispatcher):
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager

    async def dispatch(self, message: dict):
        if self.websocket_manager:
            await self.websocket_manager.broadcast(json.dumps(message))