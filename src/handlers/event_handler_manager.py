from typing import List, Any
import httpx
from ..config.settings import DispatchConfig
from ..web.websocket_manager import WebSocketManager
from .preprocessors.manager import PreprocessorManager
from .event_handler import EventHandler
from .dispatchers.manager import DispatcherManager
from .dispatchers.base import Dispatcher
from ..config.logging import logger
import json

class EventHandlerManager:
    def __init__(self,
                 dispatch_config: DispatchConfig,
                 http_client: httpx.AsyncClient,
                 websocket_manager: WebSocketManager,
                 preprocessor_manager: PreprocessorManager,
                 dispatcher_manager: DispatcherManager):
        self.event_handlers: List[EventHandler] = []
        self.default_dispatcher = dispatcher_manager.get_dispatcher({"type": "file", "path": "unhandled_messages.log"})
        self.websocket_manager = websocket_manager
        self._build_handlers(dispatch_config, http_client, websocket_manager, preprocessor_manager, dispatcher_manager)

    def _build_handlers(self, dispatch_config, http_client, websocket_manager, preprocessor_manager, dispatcher_manager):
        for i, rule_config in enumerate(dispatch_config.rules):
            preprocessor_name = rule_config.preprocessor or "base_preprocessor"
            preprocessor = preprocessor_manager.get_preprocessor(preprocessor_name)

            dispatchers: List[Dispatcher] = []
            dispatcher_types = []
            for d_config in rule_config.dispatchers:
                dispatcher = dispatcher_manager.get_dispatcher(
                    d_config,
                    http_client=http_client,
                    websocket_manager=websocket_manager
                )
                dispatchers.append(dispatcher)
                dispatcher_types.append(d_config.get("type", "unknown"))
            
            handler = EventHandler(rule_config.schema, preprocessor, dispatchers)
            self.event_handlers.append(handler)
            logger.info(f"Rule {i+1} loaded. Preprocessor: '{preprocessor.name}', Dispatchers: {', '.join(dispatcher_types)}.")

    async def handle(self, event: str, data: Any):
        for handler in self.event_handlers:
            was_handled = await handler.handle(event, data)
            if was_handled:
                return

        original_json_obj = {"event": event, "data": data}
        message_summary = json.dumps(original_json_obj)
        if len(message_summary) > 100:
            message_summary = message_summary[:100] + "..."
        logger.info(f"No matched schema, msg={message_summary}")
        await self.default_dispatcher.dispatch(original_json_obj)