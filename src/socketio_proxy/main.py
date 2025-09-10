"""
Main entry point for the Socket.IO Proxy application.
"""
import asyncio
import argparse
from socketio_proxy.core.proxy_server import SocketIOProxy
from socketio_proxy.config.settings import ConfigLoader
from socketio_proxy.config.logging import logger
from socketio_proxy.handlers.event_handler_manager import EventHandlerManager
from socketio_proxy.handlers.preprocessors.manager import PreprocessorManager
from socketio_proxy.handlers.dispatchers.manager import DispatcherManager
from socketio_proxy.web.websocket_manager import WebSocketManager
from socketio_proxy.web.route_manager import RouteManager
from socketio_proxy.core.socketio_client import SocketIOClient
from socketio_proxy.web.dependencies import app_context  # 导入 app_context
from socketio_proxy.core.proxy_builder import SocketIOProxyBuilder # 导入 SocketIOProxyBuilder
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

async def async_main():
    """
    Asynchronous main function to run the proxy from the command line.
    """
    parser = argparse.ArgumentParser(description="Socket.IO Proxy")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the YAML configuration file")
    args = parser.parse_args()

    await run_proxy_from_config(args.config)

def main():
    """
    Synchronous entry point for the command line.
    """
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Proxy terminated by user.")

if __name__ == "__main__":
    main()