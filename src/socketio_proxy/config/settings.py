import yaml
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Type

@dataclass
class ExtendConfig:
    preprocessors: List[str] = field(default_factory=list)
    routes: List[str] = field(default_factory=list)

@dataclass
class ProxyConfig:
    socketio_server_url: str
    listen_host: str
    listen_port: int
    base_url: str
    headers: Dict[str, str]

@dataclass
class DispatchRule:
    schema: Dict[str, Any]
    dispatchers: List[Dict[str, Any]]
    preprocessor: Optional[str] = None # New field for event preprocessor

@dataclass
class DispatchConfig:
    rules: List[DispatchRule] = field(default_factory=list)

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
        rules_data = dispatch_config_data.get("rules", [])
        parsed_rules = []
        for rule_data in rules_data:
            parsed_rules.append(DispatchRule(
                schema=rule_data['schema'],
                dispatchers=rule_data['dispatchers'],
                preprocessor=rule_data.get('preprocessor')
            ))
        self.dispatch_config = DispatchConfig(rules=parsed_rules)

        extend_config_data = config.get('extend', {})
        self.extend_config = ExtendConfig(
            preprocessors=extend_config_data.get('preprocessors', []),
            routes=extend_config_data.get('routes', [])
        )
