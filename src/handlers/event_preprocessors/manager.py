import importlib.util
import sys
import os
from typing import Dict
from ...config.logging import logger
from .base import BaseEventPreprocessor, base_event_preprocessor

class EventPreprocessorManager:
    """
    Manages the loading and retrieval of EventPreprocessor instances.
    Scans a specified directory for EventPreprocessor modules and registers them.
    """
    def __init__(self, preprocessors_dir: str, base_module_path: str):
        self.preprocessors: Dict[str, BaseEventPreprocessor] = {
            base_event_preprocessor.name: base_event_preprocessor
        }
        self.preprocessors_dir = preprocessors_dir
        self.base_module_path = base_module_path
        self._load_preprocessors()

    def _load_preprocessors(self):
        if not os.path.exists(self.preprocessors_dir):
            logger.warning(f"Event preprocessors directory not found: {self.preprocessors_dir}")
            return

        for filename in os.listdir(self.preprocessors_dir):
            if filename.endswith(".py") and filename not in ("__init__.py", "base.py", "manager.py"):
                module_name = filename[:-3]
                full_module_path = f"{self.base_module_path}.{module_name}"
                file_path = os.path.join(self.preprocessors_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(full_module_path, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[full_module_path] = module
                        spec.loader.exec_module(module)
                        
                        for attribute_name in dir(module):
                            attribute = getattr(module, attribute_name)
                            if isinstance(attribute, BaseEventPreprocessor):
                                if attribute.name in self.preprocessors:
                                    logger.warning(f"Duplicate event preprocessor name '{attribute.name}' found. Overwriting.")
                                self.preprocessors[attribute.name] = attribute
                                logger.info(f"Loaded event preprocessor: {attribute.name}")
                except Exception as e:
                    logger.error(f"Error loading event preprocessor from {file_path}: {e}")

    def get_preprocessor(self, name: str) -> BaseEventPreprocessor:
        """
        Retrieves an EventPreprocessor instance by its name.
        Returns the base_event_preprocessor if the named preprocessor is not found.
        """
        preprocessor = self.preprocessors.get(name)
        if not preprocessor:
            logger.warning(f"Event preprocessor '{name}' not found. Using base_event_preprocessor.")
            return self.preprocessors[base_event_preprocessor.name]
        return preprocessor