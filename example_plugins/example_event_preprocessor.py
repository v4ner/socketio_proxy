from socketio_proxy.handlers.preprocessors.base import BasePreprocessor

# 创建 BasePreprocessor 的实例
example_event_preprocessor = BasePreprocessor("example_event_preprocessor")

@example_event_preprocessor.on("ChatRoomMessage")
async def process_chat_message(data: dict) -> dict:
    # 示例逻辑：给事件数据添加一个字段
    data["X-Processed-By"] = example_event_preprocessor.name
    return data