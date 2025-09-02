"""
Main entry point for the Socket.IO Proxy application.
"""
import asyncio
import argparse
from .core.proxy_server import SocketIOProxy
from .config.settings import ConfigLoader
from .config.logging import logger
from .handlers.event_handler_manager import EventHandlerManager
from .handlers.event_preprocessors.manager import EventPreprocessorManager
from .handlers.dispatchers.manager import DispatcherManager
from .web.websocket_manager import WebSocketManager
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
    preprocessors_dir = os.path.join(os.path.dirname(__file__), 'handlers', 'event_preprocessors')
    base_module_path = 'src.handlers.event_preprocessors'
    event_preprocessor_manager = EventPreprocessorManager(preprocessors_dir, base_module_path)

    # Define the directory and module path for dispatchers
    dispatchers_dir = os.path.join(os.path.dirname(__file__), 'handlers', 'dispatchers')
    dispatchers_base_module_path = 'src.handlers.dispatchers'
    dispatcher_manager = DispatcherManager(dispatchers_dir, dispatchers_base_module_path)

    event_handler_manager = EventHandlerManager(
        config_loader.dispatch_config,
        http_client,
        websocket_manager,
        event_preprocessor_manager,
        dispatcher_manager
    )
    
    proxy = SocketIOProxy(config_loader.proxy_config, event_handler_manager)
    
    try:
        await proxy.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutting down proxy...")
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
        logger.info("Proxy terminated by user.")