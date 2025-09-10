import httpx
from socketio_proxy.handlers.dispatchers.base import Dispatcher
from socketio_proxy.config.logging import logger

class HttpDispatcher(Dispatcher):
    type = "http"

    def __init__(self, callback_url: str, http_client: httpx.AsyncClient):
        self.callback_url = callback_url
        self.http_client = http_client

    async def dispatch(self, message: dict):
        try:
            await self.http_client.post(self.callback_url, json=message)
        except httpx.RequestError as e:
            logger.error(f"HTTP dispatch error to {self.callback_url}: {e}")

    @classmethod
    def from_config(cls, config: dict, **kwargs):
        http_client = kwargs.get("http_client")
        if not http_client:
            raise ValueError("HttpDispatcher requires 'http_client' in kwargs")
        return cls(config['url'], http_client)