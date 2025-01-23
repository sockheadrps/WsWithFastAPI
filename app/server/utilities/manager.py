from fastapi import WebSocket
from typing import Dict
from server.utilities.models.models import (
    Connection,
    ConnectionResponsePayload,
    StatsEventPayload,
    EventType,
    BaseWebsocketEvent,
)
from rich.console import Console
from rich.pretty import pprint
from asyncio import sleep
from rich import print_json

console = Console()


class Manager:
    def __init__(self):
        self.active_connections: Dict[str:Connection] = {}

    async def connect(self, websocket: WebSocket) -> Connection:
        await websocket.accept()
        connection = Connection(websocket=websocket)
        self.active_connections[str(connection.client_id)] = connection

        connection_response_payload = ConnectionResponsePayload(client_id=connection.client_id)

        websocket_response = BaseWebsocketEvent(event=EventType.CONNECTION_RESPONSE, data=connection_response_payload)

        await websocket.send_json(websocket_response.model_dump_json())
        # print(websocket_response.model_dump_json())

        return connection

    async def disconnect(self, client_id: str) -> None:
        del self.active_connections[client_id]

    async def handle_message(self, connection: Connection) -> None:
        while True:
            message = await connection.websocket.receive_json()
            if message.get("event") == "CONNECT" and message.get("client") == "SERVER-STATS":
                await self.broadcast_to_client(str(connection.client_id))

    async def broadcast_to_client(self, client_id: str) -> None:
        connection: Connection = self.active_connections.get(client_id)
        if not connection:
            return
        while True:
            stats_event = StatsEventPayload(
                event=EventType.DATA_REQUEST,
            )
            print_json(data=stats_event.model_dump())
            await connection.websocket.send_json(stats_event.model_dump_json())
            await sleep(1)

    def get_active_connections(self) -> list[str]:
        return list(self.active_connections.keys())
