import asyncio
import argparse
import os
import httpx

from socketio_proxy.core.proxy_server import SocketIOProxy
from socketio_proxy.config.settings import ConfigLoader
from socketio_proxy.config.logging import logger
from socketio_proxy.handlers.event_handler_manager import EventHandlerManager
from socketio_proxy.handlers.preprocessors.manager import PreprocessorManager
from socketio_proxy.handlers.dispatchers.manager import DispatcherManager
from socketio_proxy.web.websocket_manager import WebSocketManager
from socketio_proxy.web.route_manager import RouteManager
from socketio_proxy.core.socketio_client import SocketIOClient
from socketio_proxy.web.dependencies import app_context

class SocketIOProxyBuilder:
    def __init__(self, config_path: str):
        self.config_loader = ConfigLoader(config_path)
        self.websocket_manager = WebSocketManager()
        self.http_client = httpx.AsyncClient()
        self.preprocessor_manager = self._build_preprocessor_manager()
        self.dispatcher_manager = self._build_dispatcher_manager()

    def _build_preprocessor_manager(self) -> PreprocessorManager:
        preprocessors_dir = os.path.join(os.path.dirname(__file__), '..', 'handlers', 'preprocessors')
        base_module_path = 'src.socketio_proxy.handlers.preprocessors'
        manager = PreprocessorManager(preprocessors_dir, base_module_path)
        if self.config_loader.extend_config.preprocessors:
            manager.load_from_paths(self.config_loader.extend_config.preprocessors)
        return manager

    def _build_dispatcher_manager(self) -> DispatcherManager:
        dispatchers_dir = os.path.join(os.path.dirname(__file__), '..', 'handlers', 'dispatchers')
        dispatchers_base_module_path = 'src.socketio_proxy.handlers.dispatchers'
        manager = DispatcherManager(dispatchers_dir, dispatchers_base_module_path)
        return manager

    def _build_route_manager(self) -> RouteManager:
        route_manager = RouteManager()
        if self.config_loader.extend_config.routes:
            route_manager.load_from_paths(self.config_loader.extend_config.routes)
        return route_manager

    async def build(self) -> SocketIOProxy:
        route_manager = self._build_route_manager()
        
        event_handler_manager = EventHandlerManager(
            self.config_loader.dispatch_config,
            self.http_client,
            self.websocket_manager,
            self.preprocessor_manager,
            self.dispatcher_manager
        )
 
        sio_client = SocketIOClient(
            callback_handler=event_handler_manager.handle,
            headers=self.config_loader.proxy_config.headers
        )
 
        # 注册共享实例到 app_context
        app_context.set_sio_client(sio_client)
        app_context.set_websocket_manager(self.websocket_manager)
        
        # 将加载的路由传递给 Proxy
        proxy = SocketIOProxy(
            self.config_loader.proxy_config,
            event_handler_manager,
            sio_client,
            external_routers=list(route_manager.items.values())
        )
        return proxy