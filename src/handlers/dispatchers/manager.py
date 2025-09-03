import inspect
from typing import Dict, Type, Any
from src.config.logging import logger
from src.util.reflect_manager import ReflectionManager
from .base import Dispatcher

class DispatcherManager(ReflectionManager[Type[Dispatcher]]):
    def __init__(self, dispatchers_dir: str, base_module_path: str):
        super().__init__(dispatchers_dir, base_module_path, "dispatcher")
        self._instance_cache: Dict[frozenset, Dispatcher] = {}

    @staticmethod
    def _is_concrete_dispatcher(obj: Any) -> bool:
        """检查对象是否是 Dispatcher 的一个具体子类"""
        return inspect.isclass(obj) and issubclass(obj, Dispatcher) and obj is not Dispatcher

    def _register_from_module(self, module: Any):
        for name, dispatcher_class in inspect.getmembers(module, DispatcherManager._is_concrete_dispatcher):
            if dispatcher_class.type in self.items:
                logger.warning(f"Dup dispatcher type '{dispatcher_class.type}'. Overwriting.")
            self.items[dispatcher_class.type] = dispatcher_class
            logger.info(f"Dispatcher '{name}' registered (type: '{dispatcher_class.type}').")

    def get_dispatcher(self, config: dict, **kwargs) -> Dispatcher:
        # Create a cache key from config and kwargs
        # Convert dicts to frozenset of items for hashability
        cache_key = frozenset(config.items()), frozenset(kwargs.items())

        if cache_key in self._instance_cache:
            logger.debug(f"Returning cached dispatcher for config: {config}")
            return self._instance_cache[cache_key]

        try:
            dispatcher_type = config["type"]
        except KeyError:
            raise ValueError("Dispatcher configuration must have a 'type' field.")

        dispatcher_class = self.get_item(dispatcher_type)
        if not dispatcher_class:
            raise ValueError(f"Unknown dispatcher type: '{dispatcher_type}'")
            
        instance = dispatcher_class.from_config(config, **kwargs)
        self._instance_cache[cache_key] = instance
        logger.debug(f"Created and cached new dispatcher for config: {config}")
        return instance