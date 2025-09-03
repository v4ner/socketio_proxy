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
from .core.proxy_builder import SocketIOProxyBuilder # 导入 SocketIOProxyBuilder
import httpx
import os

async def run_proxy_from_config(config_path: str):
    """
    Runs the Socket.IO proxy with a given configuration file.
    This function can be directly called from a Jupyter Notebook.
    """
    builder = SocketIOProxyBuilder(config_path)
    proxy = await builder.build()
    try:
        await proxy.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Proxy shutting down...")
    finally:
        await proxy.stop()
        await builder.http_client.aclose() # Ensure http_client is closed

async def main():
    """
    Main function to run the proxy from the command line.
    """
    parser = argparse.ArgumentParser(description="Socket.IO Proxy")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the YAML configuration file")
    args = parser.parse_args()

    run_proxy_from_config(args.config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Proxy terminated.")