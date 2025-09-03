from typing import Optional
from .base import BasePreprocessor
from src.config.logging import logger

# Create an instance of BasePreprocessor
chat_preprocessor = BasePreprocessor("chat_message_preprocessor")

@chat_preprocessor.on("ChatRoomMessage")
def preprocess_chat_room_message(data: dict) -> Optional[dict]:
    """
    Example preprocessor for 'ChatRoomMessage' event.
    It removes the 'Sender' and 'Target' fields from the data.
    """
    logger.info(f"Preprocessing ChatRoomMessage with chat_message_preprocessor. Original data: {data}")

    # Example interception logic: if message contains "intercept", drop it.
    if "message" in data and data["message"] == "intercept":
        logger.info("Message contains 'intercept' keyword. Dropping message.")
        return None

    if "Sender" in data:
        del data["Sender"]
    if "Target" in data:
        del data["Target"]
    logger.info(f"Modified data: {data}")
    return data
