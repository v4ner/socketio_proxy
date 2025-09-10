# Socket.IO 代理

高度可配置、可扩展的 Socket.IO 代理服务，可以拦截、预处理和分发 Socket.IO 事件，把持久连接的数据流转换为纯粹的事件驱动

## 特性

- **Socket.IO 代理**: 代理客户端和 Socket.IO 服务器之间的流量。
- **事件分发**: 根据可配置的规则将事件分发到不同的目标（例如，文件、HTTP 端点）。
- **事件预处理**: 在分发之前修改事件。
- **可扩展**: 通过插件轻松添加自定义的预处理器和 API 路由。
- **基于配置**: 使用 YAML 文件轻松配置所有内容。

## 安装

1.  克隆此仓库：
    ```bash
    git clone <repository-url>
    cd socketio_proxy
    ```

2.  安装依赖项：
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

1.  复制示例配置文件：
    ```bash
    cp config.yaml.example config.yaml
    ```

2.  根据您的需求编辑 `config.yaml`。有关详细信息，请参阅[配置](#配置)部分。

3.  运行代理服务器：
    ```bash
    ./run.sh
    ```
    或者，您可以直接运行 Python 模块：
    ```bash
    python3 -m src.socketio_proxy.main --config config.yaml
    ```

## 配置

代理服务器使用 `config.yaml` 文件进行配置。有关所有可用选项的详细说明，请参阅 [`config.yaml.example`](config.yaml.example)。

### `proxy`

-   `socketio_server_url`: 要代理的 Socket.IO 服务器的 URL。
-   `listen_host`: 代理服务器监听的主机。
-   `listen_port`: 代理服务器监听的端口。
-   `base_url`: (可选) 代理服务器的基础 URL 路径。
-   `headers`: (可选) 转发到目标服务器时要添加的自定义请求头。

### `dispatch`

-   `rules`: 基于其 schema 将事件路由到不同分发器的规则列表。
    -   `schema`: 用于匹配事件的 JSON schema。空 schema (`{}`) 将匹配所有事件。
    -   `dispatchers`: 此规则的分发器列表。
        -   `type`: 分发器类型（例如，`file`、`http`、`websocket`）。
        -   `target`: 分发目标（例如，文件名、URL）。
    -   `preprocessor`: (可选) 在分发之前应用于事件的预处理器的名称。

### `extend`

-   `preprocessors`: (可选) 要加载的自定义预处理器模块的列表。
-   `routes`: (可选) 要加载的自定义 FastAPI 路由模块的列表。

## Web 界面

代理服务器在根 URL (`/`) 上提供了一个 Web 界面，可用于实时查看 Socket.IO 事件流。

主要功能：
- **实时事件流**: 查看所有传入和传出的 Socket.IO 事件。
- **事件筛选**: 按事件名称筛选显示的事件。
- **消息发送器**: 通过表单或原始 JSON 向 Socket.IO 服务器发送消息。
- **连接管理**: 重启与 Socket.IO 服务器的连接。

要访问 Web 界面，请在浏览器中打开代理服务器的地址（例如，`http://localhost:3080`）。

## HTTP API

代理服务器还公开了几个 HTTP API 端点：

- `POST /send_message`: 通过 HTTP 发送 Socket.IO 事件。
  - **请求体**: `{"event": "your_event", "data": {"key": "value"}}`
- `POST /restart_sio`: 重启与 Socket.IO 服务器的连接。

## 插件开发

您可以通过创建自定义的事件预处理器和 API 路由来扩展代理的功能。

### 自定义事件预处理器

事件预处理器允许您在事件分发之前对其进行修改。

1.  创建一个继承自 `src.socketio_proxy.handlers.preprocessors.base.BasePreprocessor` 的新 Python 文件。
2.  使用 `@your_preprocessor.on("event_name")` 装饰器为特定事件注册处理函数。
3.  在 `config.yaml` 的 `extend.preprocessors` 部分添加您的预处理器模块的路径。

**示例 (`plugins/my_preprocessor.py`):**
```python
from socketio_proxy.handlers.preprocessors.base import BasePreprocessor

my_preprocessor = BasePreprocessor("my_preprocessor")

@my_preprocessor.on("chat_message")
def process_chat_message(data: dict) -> dict:
    data["processed"] = True
    return data
```

### 自定义 API 路由

您可以添加自己的 FastAPI 路由来创建自定义的 HTTP API 端点。

1.  创建一个新的 Python 文件并定义一个 FastAPI `APouter`。
2.  在 `config.yaml` 的 `extend.routes` 部分添加您的路由模块的路径。

**示例 (`plugins/my_api.py`):**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/my_endpoint")
async def my_endpoint():
    return {"message": "Hello from my custom API!"}
```