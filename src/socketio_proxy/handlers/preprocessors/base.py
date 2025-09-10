from typing import Callable, Dict, Any, Optional, Coroutine

class BasePreprocessor:
    """
    Base class for event preprocessors.
    Each preprocessor instance has a name and can register multiple preprocessor functions
    for different event types.
    """
    def __init__(self, name: str):
        self.name = name
        self._preprocessors: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, Optional[Dict[str, Any]]]]] = {}

    def on(self, event_name: str) -> Callable:
        """
        Decorator to register a preprocessor function for a specific event.
        The preprocessor function should take 'data' (dict) as input and return
        the modified 'data' (dict).
        """
        def decorator(func: Callable[[Dict[str, Any]], Coroutine[Any, Any, Optional[Dict[str, Any]]]]) -> Callable[[Dict[str, Any]], Coroutine[Any, Any, Optional[Dict[str, Any]]]]:
            self._preprocessors[event_name] = func
            return func
        return decorator

    async def preprocess(self, event: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Preprocesses the event data using the registered preprocessor function.
        If no preprocessor is registered for the event, the data is returned as is.
        """
        preprocessor_func = self._preprocessors.get(event)
        if preprocessor_func:
            return await preprocessor_func(data)
        return data

# Default event preprocessor that does not modify any events
base_preprocessor = BasePreprocessor("base_preprocessor")