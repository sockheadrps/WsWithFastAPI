import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from server.utilities.models.models import (
    Connection,
    StatsEvent,
    StatsPayload,
    EventType,
    BaseWebsocketEvent,
)
from .stats import Computer
from rich.console import Console
from rich.pretty import pprint
from asyncio import sleep

console = Console()


class Manager:
    def __init__(self):
        pass

    async def connect(self, websocket: WebSocket) -> Connection:
        pass

    async def disconnect(self, client_id: str) -> None:
        pass

    async def handle_message(self, connection: Connection) -> None:
        pass

    async def broadcast_to_client(self, client_id: str) -> None:
        pass

    def get_active_connections(self) -> list[str]:
        pass
