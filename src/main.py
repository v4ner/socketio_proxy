"""
Main entry point for the Socket.IO Proxy application.
"""
import asyncio
import argparse
from .core.proxy_server import SocketIOProxy
from .config.settings import ConfigLoader
from .config.logging import logger
from .handlers.event_handler_manager import EventHandlerManager
from .handlers.preprocessors.manager import PreprocessorManager
from .handlers.dispatchers.manager import DispatcherManager
from .web.websocket_manager import WebSocketManager
from .web.route_manager import RouteManager
from .core.socketio_client import SocketIOClient
from .web.dependencies import app_context  # 导入 app_context
import httpx
import os

async def run_proxy_from_config(config_path: str):
    """
    Runs the Socket.IO proxy with a given configuration file.
    This function can be directly called from a Jupyter Notebook.
    """
    config_loader = ConfigLoader(config_path)
    
    websocket_manager = WebSocketManager()
    http_client = httpx.AsyncClient()

    # Define the directory and module path for event preprocessors
    preprocessors_dir = os.path.join(os.path.dirname(__file__), 'handlers', 'preprocessors')
    base_module_path = 'src.handlers.preprocessors'
    preprocessor_manager = PreprocessorManager(preprocessors_dir, base_module_path)
 
    # Define the directory and module path for dispatchers
    dispatchers_dir = os.path.join(os.path.dirname(__file__), 'handlers', 'dispatchers')
    dispatchers_base_module_path = 'src.handlers.dispatchers'
    dispatcher_manager = DispatcherManager(dispatchers_dir, dispatchers_base_module_path)

    # 新增: 加载外部模块
    # 1. 加载外部 preprocessors
    if config_loader.extend_config.preprocessors:
        preprocessor_manager.load_from_paths(config_loader.extend_config.preprocessors)

    # 2. 加载外部 routes
    route_manager = RouteManager()
    
    event_handler_manager = EventHandlerManager(
        config_loader.dispatch_config,
        http_client,
        websocket_manager,
        preprocessor_manager,
        dispatcher_manager
    )

    sio_client = SocketIOClient(
        callback_handler=event_handler_manager.handle,
        headers=config_loader.proxy_config.headers
    )

    # 注册共享实例到 app_context
    app_context.set_sio_client(sio_client)
    app_context.set_websocket_manager(websocket_manager)

    if config_loader.extend_config.routes:
        route_manager.load_from_paths(config_loader.extend_config.routes)
    
    # 将加载的路由传递给 Proxy
    proxy = SocketIOProxy(
        config_loader.proxy_config,
        event_handler_manager,
        sio_client,
        external_routers=list(route_manager.items.values())
    )
    
    try:
        await proxy.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Proxy shutting down...")
    finally:
        await proxy.stop()
        await http_client.aclose() # Ensure http_client is closed

async def main():
    """
    Main function to run the proxy from the command line.
    """
    parser = argparse.ArgumentParser(description="Socket.IO Proxy")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the YAML configuration file")
    args = parser.parse_args()

    await run_proxy_from_config(args.config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Proxy terminated.")