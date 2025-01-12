import asyncio
import random
from typing import Any, Dict
import websockets
from app.models.models import WebsocketData, WebsocketEvent


class Client:
    def __init__(self, websocket_url: str):
        pass

    async def connect(self):
        pass

    async def send(self, event: str, data: Dict[str, Any] = None):
        pass

    async def recv(self) -> WebsocketEvent:
        pass


async def handle_client(client: Client):
    pass


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
