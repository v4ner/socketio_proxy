import sys
import inspect
from typing import Dict, Any
from socketio_proxy.config.logging import logger
from socketio_proxy.util.reflection_manager import ReflectionManager
from socketio_proxy.handlers.preprocessors.base import BasePreprocessor, base_preprocessor

class PreprocessorManager(ReflectionManager[BasePreprocessor]):
    def __init__(self, preprocessors_dir: str, base_module_path: str):
        super().__init__(preprocessors_dir, base_module_path, "preprocessor")
        self.items[base_preprocessor.name] = base_preprocessor

    def _register_from_module(self, module: Any):
        for name, instance in inspect.getmembers(module, lambda obj: isinstance(obj, BasePreprocessor)):
            if instance.name in self.items:
                logger.warning(f"Dup preprocessor '{instance.name}'. Overwriting.")
            self.items[instance.name] = instance
            logger.info(f"Preprocessor '{name}' (instance name: '{instance.name}') loaded.")

    def get_preprocessor(self, name: str) -> BasePreprocessor:
        preprocessor = self.get_item(name)
        if not preprocessor:
            logger.warning(f"Preprocessor '{name}' not found. Using base.")
            return self.items[base_preprocessor.name]
        return preprocessor