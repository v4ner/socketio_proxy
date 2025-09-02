from jsonschema import validate, ValidationError
from typing import List, Dict, Any
from .dispatchers.base import Dispatcher
from .event_preprocessors.base import BaseEventPreprocessor
from ..config.logging import logger
import json
import asyncio

class EventHandler:
    def __init__(self, schema: Dict[str, Any], event_preprocessor: BaseEventPreprocessor, dispatchers: List[Dispatcher]):
        self.schema = schema
        self.event_preprocessor = event_preprocessor
        self.dispatchers = dispatchers

    async def handle(self, event: str, data: Any) -> bool:
        """
        Attempts to handle the event.
        Returns True if the event matched the schema and was handled, False otherwise.
        """
        json_obj = {"event": event, "data": data}
        try:
            validate(instance=json_obj, schema=self.schema)
            
            # Schema matched, proceed with preprocessing and dispatching
            logger.info(f"Event matched schema. Applying preprocessor '{self.event_preprocessor.name}'...")
            processed_data = self.event_preprocessor.preprocess(event, data)
            final_json_obj = {"event": event, "data": processed_data}

            message_summary = json.dumps(final_json_obj)
            if len(message_summary) > 100:
                message_summary = message_summary[:100] + "..."
            logger.info(f"Dispatching to {len(self.dispatchers)} dispatcher(s). Message summary: {message_summary}")

            await asyncio.gather(*(d.dispatch(final_json_obj) for d in self.dispatchers))
            
            return True # Event was handled
        except ValidationError:
            return False # Schema did not match