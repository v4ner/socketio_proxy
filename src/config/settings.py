import yaml
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ProxyConfig:
    socketio_server_url: str
    listen_host: str
    listen_port: int
    base_url: str
    headers: Dict[str, str]

@dataclass
class DispatchConfig:
    rules: List[Dict[str, Any]] = field(default_factory=list)

class ConfigLoader:
    def __init__(self, config_path=None):
        config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

        proxy_config_data = config.get('proxy', {})
        self.proxy_config = ProxyConfig(
            socketio_server_url=proxy_config_data.get("socketio_server_url", os.getenv("SOCKETIO_SERVER_URL", "http://localhost:5000")),
            listen_host=proxy_config_data.get("listen_host", os.getenv("LISTEN_HOST", "0.0.0.0")),
            listen_port=int(proxy_config_data.get("listen_port", os.getenv("LISTEN_PORT", "3080"))),
            base_url=proxy_config_data.get("base_url", os.getenv("BASE_URL", "")),
            headers=proxy_config_data.get("headers", {})
        )

        if self.proxy_config.base_url and not self.proxy_config.base_url.startswith('/'):
            self.proxy_config.base_url = '/' + self.proxy_config.base_url

        dispatch_config_data = config.get('dispatch', {})
        self.dispatch_config = DispatchConfig(
            rules=dispatch_config_data.get("rules", [])
        )
