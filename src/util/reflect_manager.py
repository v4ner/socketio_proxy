import os
import importlib.util
import sys
from abc import ABC, abstractmethod
from typing import Dict, TypeVar, Generic, Any
from src.config.logging import logger

# 定义一个类型变量，用于泛型，可以是任何类型
T = TypeVar('T')

class ReflectionManager(ABC, Generic[T]):
    """
    A generic manager for dynamically loading modules and registering objects (instances or classes)
    based on reflection. Subclasses must implement the _register_from_module method.
    """
    def __init__(self, target_dir: str, base_module_path: str, item_name: str):
        self.items: Dict[str, T] = {}
        self.target_dir = target_dir
        self.base_module_path = base_module_path
        self.item_name = item_name # e.g., "preprocessor", "dispatcher"
        self._load_items()

    def _load_items(self):
        if not os.path.exists(self.target_dir):
            logger.warning(f"{self.item_name.capitalize()} dir not found: {self.target_dir}")
            return

        for filename in os.listdir(self.target_dir):
            if filename.endswith(".py") and filename not in ("__init__.py", "base.py", "manager.py", "reflect_manager.py"):
                module_name = filename[:-3]
                full_module_path = f"{self.base_module_path}.{module_name}"
                file_path = os.path.join(self.target_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(full_module_path, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[full_module_path] = module
                        spec.loader.exec_module(module)
                        self._register_from_module(module)
                except Exception as e:
                    logger.error(f"Load {self.item_name} fail '{file_path}': {e}")

    @abstractmethod
    def _register_from_module(self, module: Any):
        """
        Abstract method to be implemented by subclasses to define how to extract and register
        items from a loaded module.
        """
        pass

    def get_item(self, name: str) -> T:
        """
        Retrieves an item by its name.
        """
        item = self.items.get(name)
        if not item:
            logger.warning(f"{self.item_name.capitalize()} '{name}' not found.")
        return item