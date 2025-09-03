from jsonschema import validate, ValidationError
from typing import List, Dict, Any
from .dispatchers.base import Dispatcher
from .preprocessors.base import BasePreprocessor
from ..config.logging import logger
import json
import asyncio

class EventHandler:
    def __init__(self, schema: Dict[str, Any], preprocessor: BasePreprocessor, dispatchers: List[Dispatcher]):
        self.schema = schema
        self.preprocessor = preprocessor
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
            logger.info(f"Event matched schema. Applying preprocessor '{self.preprocessor.name}'...")
            processed_data = self.preprocessor.preprocess(event, data)
            if processed_data is None:
                logger.info(f"Preprocessor '{self.preprocessor.name}' intercepted event '{event}'. Message dropped.")
                return True # Event was handled (intercepted)

            final_json_obj = {"event": event, "data": processed_data}

            message_summary = json.dumps(final_json_obj)
            if len(message_summary) > 100:
                message_summary = message_summary[:100] + "..."
            logger.info(f"Dispatching to {len(self.dispatchers)} dispatcher(s). Message summary: {message_summary}")

            await asyncio.gather(*(d.dispatch(final_json_obj) for d in self.dispatchers))
            
            return True # Event was handled
        except ValidationError:
            return False # Schema did not match