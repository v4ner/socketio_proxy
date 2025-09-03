"""
Centralized dependency management for the web components.

This module provides a global context (`app_context`) that holds shared
instances of services like the SocketIOClient, WebSocketManager, etc.,
which are primarily used by the web routes and plugins.
"""
from typing import Optional, Dict, Any
from src.core.socketio_client import SocketIOClient
from src.web.websocket_manager import WebSocketManager

class AppContext:
    """
    A singleton-like class to hold and provide access to shared application components.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppContext, cls).__new__(cls)
            cls._instance.sio_client: Optional[SocketIOClient] = None
            cls._instance.websocket_manager: Optional[WebSocketManager] = None
            cls._instance.custom_data: Dict[str, Any] = {}
        return cls._instance

    def set_sio_client(self, client: SocketIOClient):
        """Registers the Socket.IO client instance."""
        self.sio_client = client

    def get_sio_client(self) -> SocketIOClient:
        """Retrieves the Socket.IO client instance."""
        if not self.sio_client:
            raise RuntimeError("SocketIOClient has not been initialized in the app context.")
        return self.sio_client

    def set_websocket_manager(self, manager: WebSocketManager):
        """Registers the WebSocketManager instance."""
        self.websocket_manager = manager

    def get_websocket_manager(self) -> WebSocketManager:
        """Retrieves the WebSocketManager instance."""
        if not self.websocket_manager:
            raise RuntimeError("WebSocketManager has not been initialized in the app context.")
        return self.websocket_manager
    
    def set_custom_data(self, key: str, value: Any):
        """Stores custom data in the context."""
        self.custom_data[key] = value

    def get_custom_data(self, key: str) -> Any:
        """Retrieves custom data from the context."""
        return self.custom_data.get(key)

# Global instance of the application context
app_context = AppContext()