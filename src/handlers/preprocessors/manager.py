import sys
from typing import Dict, Any
from src.config.logging import logger
from src.util.reflect_manager import ReflectionManager
from .base import BasePreprocessor, base_preprocessor

class PreprocessorManager(ReflectionManager[BasePreprocessor]):
    def __init__(self, preprocessors_dir: str, base_module_path: str):
        super().__init__(preprocessors_dir, base_module_path, "preprocessor")
        self.items[base_preprocessor.name] = base_preprocessor

    def _register_from_module(self, module: Any):
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, BasePreprocessor):
                if attribute.name in self.items:
                    logger.warning(f"Dup preprocessor '{attribute.name}'. Overwriting.")
                self.items[attribute.name] = attribute
                logger.info(f"Preprocessor '{attribute.name}' loaded.")

    def get_preprocessor(self, name: str) -> BasePreprocessor:
        preprocessor = self.get_item(name)
        if not preprocessor:
            logger.warning(f"Preprocessor '{name}' not found. Using base.")
            return self.items[base_preprocessor.name]
        return preprocessor