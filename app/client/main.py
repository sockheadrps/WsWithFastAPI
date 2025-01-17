import asyncio
import random
from typing import Any, Dict
import websockets
from models.models import WebsocketData, WebsocketEvent


class Client:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.websocket = None
        self.client_id = None

    async def connect(self):
        self.websocket = await websockets.connect(self.websocket_url)
        connection_event = WebsocketEvent(
            event="connect",
            client_id="",
            data=WebsocketData(data={})
        )
        await self.websocket.send(connection_event.model_dump_json())
        response = WebsocketEvent.model_validate_json(await self.websocket.recv())
        self.client_id = response.client_id

    async def send(self, event: str, data: Dict[str, Any] = None):
        event = WebsocketEvent(
            event=event,
            client_id=self.client_id,
            data=WebsocketData(data=data)
        )
        print(event.model_dump_json())
        await self.websocket.send(event.model_dump())

    async def recv(self) -> WebsocketEvent:
        return WebsocketEvent.model_validate_json(await self.websocket.recv())


async def handle_client(client: Client):
    await client.connect()

    while True:
        event = await client.recv()
        print(f"Client {client.client_id} received event: {event.model_dump()}")


async def main():
    clients = []
    for _ in range(10):
        client = Client("ws://localhost:8000/ws/py_client")
        clients.append(client)
    
    await asyncio.gather(*[handle_client(client) for client in clients])


if __name__ == "__main__":
    asyncio.run(main())
