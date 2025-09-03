import importlib.util
import sys
import os
import inspect
from typing import List, Dict, Any
from fastapi import APIRouter
from src.config.logging import logger

class RouteManager:
    def __init__(self):
        self.routers: List[APIRouter] = []

    def load_routes_from_paths(self, paths: List[str], context: Dict[str, Any]):
        for path in paths:
            if not os.path.exists(path):
                logger.warning(f"Route file not found: {path}")
                continue
            
            module_name = os.path.splitext(os.path.basename(path))[0]
            full_module_path = f"external.routes.{module_name}"
            
            try:
                spec = importlib.util.spec_from_file_location(full_module_path, path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[full_module_path] = module
                    spec.loader.exec_module(module)
                    self._initialize_and_register(module, context)
            except Exception as e:
                logger.error(f"Failed to load routes from '{path}': {e}")

    def _initialize_and_register(self, module: Any, context: Dict[str, Any]):
        # 检查并调用初始化函数
        if hasattr(module, "initialize_plugin"):
            try:
                module.initialize_plugin(context)
                logger.info(f"Initialized plugin in module '{module.__name__}' with context.")
            except Exception as e:
                logger.error(f"Failed to initialize plugin in '{module.__name__}': {e}")
        
        # 注册 APIRouter 实例
        for name, member in inspect.getmembers(module, lambda obj: isinstance(obj, APIRouter)):
            self.routers.append(member)
            logger.info(f"Loaded external router '{name}' from module '{module.__name__}'.")