from .base import BaseEventPreprocessor
from src.config.logging import logger

# Create an instance of BaseEventPreprocessor
chat_preprocessor = BaseEventPreprocessor("chat_message_preprocessor")

@chat_preprocessor.on("ChatRoomMessage")
def preprocess_chat_room_message(data: dict) -> dict:
    """
    Example preprocessor for 'ChatRoomMessage' event.
    It removes the 'Sender' and 'Target' fields from the data.
    """
    logger.info(f"Preprocessing ChatRoomMessage with chat_message_preprocessor. Original data: {data}")
    if "Sender" in data:
        del data["Sender"]
    if "Target" in data:
        del data["Target"]
    logger.info(f"Modified data: {data}")
    return data
