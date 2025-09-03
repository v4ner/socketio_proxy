import os
import importlib
import inspect
from typing import Dict, Type
from src.config.logging import logger
from .base import Dispatcher

class DispatcherManager:
    def __init__(self, dispatchers_dir: str, base_module_path: str):
        self.dispatchers: Dict[str, Type[Dispatcher]] = {}
        self._discover_dispatchers(dispatchers_dir, base_module_path)

    def _discover_dispatchers(self, dispatchers_dir: str, base_module_path: str):
        for filename in os.listdir(dispatchers_dir):
            if filename.endswith(".py") and filename not in ("__init__.py", "base.py", "manager.py"):
                module_name = filename[:-3]
                module_path = f"{base_module_path}.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, Dispatcher) and obj is not Dispatcher:
                            if obj.type in self.dispatchers:
                                logger.warning(f"Dup dispatcher type '{obj.type}'. Overwriting.")
                            self.dispatchers[obj.type] = obj
                            logger.info(f"Dispatcher '{name}' registered (type: '{obj.type}').")
                except ImportError as e:
                    logger.error(f"Import dispatcher fail '{module_path}': {e}")

    def get_dispatcher(self, config: dict, **kwargs) -> Dispatcher:
        dispatcher_type = config.get("type")
        if not dispatcher_type:
            raise ValueError("Dispatcher configuration must have a 'type' field.")
        
        dispatcher_class = self.dispatchers.get(dispatcher_type)
        if not dispatcher_class:
            raise ValueError(f"Unknown dispatcher type: {dispatcher_type}")
            
        return dispatcher_class.from_config(config, **kwargs)