import aiofiles
import json
from .base import Dispatcher

class FileDispatcher(Dispatcher):
    type = "file"

    def __init__(self, file_path: str):
        self.file_path = file_path

    async def dispatch(self, message: dict):
        async with aiofiles.open(self.file_path, mode='a') as f:
            await f.write(json.dumps(message) + '\n')

    @classmethod
    def from_config(cls, config: dict, **kwargs):
        return cls(config['path'])