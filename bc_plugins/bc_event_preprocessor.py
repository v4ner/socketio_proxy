from src.handlers.preprocessors.base import BasePreprocessor

class BcEventPreprocessor(BasePreprocessor):
    def __init__(self):
        super().__init__("bc_event_preprocessor")
        self.on("ChatRoomMessage")(self.process_chat_message)

    def process_chat_message(self, data: dict) -> dict:
        # 示例逻辑：给事件数据添加一个字段
        data["X-Processed-By"] = self.name
        return data


bc_event_preprocessor = BcEventPreprocessor()