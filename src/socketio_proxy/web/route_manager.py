import importlib.util
import sys
import os
import inspect
from typing import List, Dict, Any, Type
from fastapi import APIRouter
from socketio_proxy.config.logging import logger
from socketio_proxy.util.reflection_manager import ReflectionManager

class RouteManager(ReflectionManager[APIRouter]):
    def __init__(self, route_dir: str = "", base_module_path: str = "src.socketio_proxy.web.routes"):
        super().__init__(route_dir, base_module_path, "route")

    def _register_from_module(self, module: Any):
        if hasattr(module, "initialize_plugin"):
            try:
                module.initialize_plugin()
                logger.info(f"Initialized plugin in module '{module.__name__}'.")
            except Exception as e:
                logger.error(f"Failed to initialize plugin in '{module.__name__}': {e}")
        
        for name, member in inspect.getmembers(module, lambda obj: isinstance(obj, APIRouter)):
            self.items[name] = member
            logger.info(f"Loaded external router '{name}' from module '{module.__name__}'.")