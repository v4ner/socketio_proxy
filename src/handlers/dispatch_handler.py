from jsonschema import validate, ValidationError
from ..config.logging import logger
from .dispatchers import Dispatcher, FileDispatcher, HttpDispatcher, WebSocketDispatcher
from ..config.settings import DispatchConfig
from ..web.websocket_manager import WebSocketManager
import json
from typing import List, Dict, Any
import httpx

class DispatchHandler:
    def __init__(self, dispatch_config: DispatchConfig, http_client: httpx.AsyncClient, websocket_manager: WebSocketManager):
        self.rules: Dict[str, List[Dispatcher]] = {}
        self.default_dispatcher = FileDispatcher("message.log")
        self.http_client = http_client
        self.websocket_manager = websocket_manager
        self._configure_dispatchers(dispatch_config)

    def _configure_dispatchers(self, dispatch_config: DispatchConfig):
        for i, rule in enumerate(dispatch_config.rules):
            schema = rule['schema']
            dispatchers_config = rule['dispatchers']
            
            dispatchers = []
            dispatcher_types = []
            for d_config in dispatchers_config:
                if d_config['type'] == 'http':
                    dispatchers.append(HttpDispatcher(d_config['url'], self.http_client))
                    dispatcher_types.append('http')
                elif d_config['type'] == 'websocket':
                    dispatchers.append(WebSocketDispatcher(self.websocket_manager))
                    dispatcher_types.append('websocket')
                elif d_config['type'] == 'file':
                    dispatchers.append(FileDispatcher(d_config['path']))
                    dispatcher_types.append('file')
            
            logger.info(f"第 {i+1} 个规则加载了 {', '.join(dispatcher_types)} 类型的 dispatcher(s)。")
            self.register(schema, dispatchers)

    def register(self, schema: Dict[str, Any], dispatchers: List[Dispatcher]):
        # Using the schema's string representation as a key.
        # This is a simplification. A more robust approach might involve schema IDs.
        schema_key = json.dumps(schema, sort_keys=True)
        self.rules[schema_key] = dispatchers

    async def handle(self, event: str, data: Any):
        json_obj = {"event": event, "data": data}
        
        dispatched = False
        for schema_key, dispatchers in self.rules.items():
            schema = json.loads(schema_key)
            try:
                validate(instance=json_obj, schema=schema)
                message_summary = json.dumps(json_obj)
                if len(message_summary) > 100:
                    message_summary = message_summary[:100] + "..."
                logger.info(f"Dispatching to {len(dispatchers)} dispatcher(s). Message summary: {message_summary}")
                for dispatcher in dispatchers:
                    await dispatcher.dispatch(json_obj)
                dispatched = True
            except ValidationError:
                continue
        
        if not dispatched:
            message_summary = json.dumps(json_obj)
            if len(message_summary) > 100:
                message_summary = message_summary[:100] + "..."
            logger.info(f"Using default dispatcher. Message summary: {message_summary}")
            await self.default_dispatcher.dispatch(json_obj)
