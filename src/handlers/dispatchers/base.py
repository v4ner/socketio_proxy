from abc import ABC, abstractmethod

class Dispatcher(ABC):
    """Abstract base class for all dispatchers."""
    
    # A class-level attribute to identify the dispatcher type in config.yaml
    type: str = "base"

    @abstractmethod
    async def dispatch(self, message: dict):
        """Dispatches the message."""
        pass

    @classmethod
    def from_config(cls, config: dict, **kwargs):
        """Creates a dispatcher instance from its configuration."""
        raise NotImplementedError