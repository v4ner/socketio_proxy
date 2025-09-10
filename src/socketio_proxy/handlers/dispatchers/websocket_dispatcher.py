import json
from socketio_proxy.handlers.dispatchers.base import Dispatcher
from socketio_proxy.web.websocket_manager import WebSocketManager

class WebSocketDispatcher(Dispatcher):
    type = "websocket"

    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager

    async def dispatch(self, message: dict):
        if self.websocket_manager:
            await self.websocket_manager.broadcast(json.dumps(message))

    @classmethod
    def from_config(cls, config: dict, **kwargs):
        websocket_manager = kwargs.get("websocket_manager")
        if not websocket_manager:
            raise ValueError("WebSocketDispatcher requires 'websocket_manager' in kwargs")
        return cls(websocket_manager)