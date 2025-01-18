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
        self.active_connections: Dict[str, Connection] = {}
        self.connected_services: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket) -> Connection:
        """Establish new websocket connection and return connection details"""
        await websocket.accept()
        connection = Connection(websocket=websocket)
        self.active_connections[str(connection.client_id)] = connection

        # Send initial connect event
        connect_event = BaseWebsocketEvent(
            client_id=connection.client_id,
            event="CONNECT",
            payload={}
        )
        pprint(connect_event)
        await websocket.send_json(connect_event.model_dump_json())

        return connection

    async def disconnect(self, client_id: str) -> None:
        if client_id in self.active_connections:
            connection = self.active_connections.pop(client_id)
            websocket_key = connection.websocket.headers.get("sec-websocket-key")
            if websocket_key in self.connected_services:
                self.connected_services.pop(websocket_key)
            await connection.websocket.close()
            pprint({"action": "disconnect", "client_id": client_id, "timestamp": datetime.now().isoformat()})

    async def handle_message(self, connection: Connection) -> None:
        """Handle incoming websocket messages"""
        try:
            while True:
                message = await connection.websocket.receive_json()

                if message.get("event") == "CONNECT" and message.get("client") == "SERVER-STATS":
                    websocket_key = connection.websocket.headers["sec-websocket-key"]
                    self.connected_services[websocket_key] = "SERVER-STATS"
                    await self.broadcast_to_client(str(connection.client_id))

        except WebSocketDisconnect:
            await self.disconnect(str(connection.client_id))
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON received[/red]")
        except Exception as e:
            console.print(f"[red]Error processing message: {str(e)}[/red]")
            await self.disconnect(str(connection.client_id))

    async def broadcast_to_client(self, client_id: str) -> None:
        """Stream system stats to a specific client"""
        try:
            connection = self.active_connections.get(str(client_id))
            if not connection:
                return

            while True:
                stats_event = StatsEvent(
                    client_id=client_id,
                    event=EventType.DATA_REQUEST,
                    data=StatsPayload(**Computer.get_stats_dict()),
                )

                pprint(stats_event.model_dump())
                await connection.websocket.send_json(stats_event.model_dump())
                await sleep(1)

        except WebSocketDisconnect:
            await self.disconnect(client_id)
        except Exception as e:
            console.print(f"[red]Error broadcasting to client {client_id}: {str(e)}[/red]")
            await self.disconnect(client_id)

    def get_active_connections(self) -> list[str]:
        """Get list of active connection IDs"""
        return list(self.active_connections.keys())
