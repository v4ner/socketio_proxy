from src.handlers.preprocessors.base import BasePreprocessor

# 创建 BasePreprocessor 的实例
bc_event_preprocessor = BasePreprocessor("bc_event_preprocessor")

@bc_event_preprocessor.on("ChatRoomMessage")
def process_chat_message(data: dict) -> dict:
    # 示例逻辑：给事件数据添加一个字段
    data["X-Processed-By"] = bc_event_preprocessor.name
    return data