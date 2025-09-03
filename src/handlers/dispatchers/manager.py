import inspect
from typing import Dict, Type, Any
from src.config.logging import logger
from src.util.reflect_manager import ReflectionManager
from .base import Dispatcher

class DispatcherManager(ReflectionManager[Type[Dispatcher]]):
    def __init__(self, dispatchers_dir: str, base_module_path: str):
        super().__init__(dispatchers_dir, base_module_path, "dispatcher")

    def _register_from_module(self, module: Any):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Dispatcher) and obj is not Dispatcher:
                if obj.type in self.items:
                    logger.warning(f"Dup dispatcher type '{obj.type}'. Overwriting.")
                self.items[obj.type] = obj
                logger.info(f"Dispatcher '{name}' registered (type: '{obj.type}').")

    def get_dispatcher(self, config: dict, **kwargs) -> Dispatcher:
        dispatcher_type = config.get("type")
        if not dispatcher_type:
            raise ValueError("Dispatcher configuration must have a 'type' field.")
        
        dispatcher_class = self.get_item(dispatcher_type)
        if not dispatcher_class:
            raise ValueError(f"Unknown dispatcher type: {dispatcher_type}")
            
        return dispatcher_class.from_config(config, **kwargs)