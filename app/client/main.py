import asyncio
import json
import random
from typing import Any, Dict
import uuid
import websockets
from pydantic import ValidationError
from models.models import (
    BaseWebsocketEvent,
    ConnectionResponseEvent,
    PingEvent,
    PingResponseEvent,
    ClientType,
    EventType,
    ClientConnectionRequestEvent,
)
from rich import print_json
from rich.console import Console

# Initialize Rich Console for logging
console = Console()


class Client:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.websocket = None
        self.client_id: str = ""

    async def connect(self):
        """Connect to the WebSocket server and establish a client ID."""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            console.print("[bold green]Connected to the server.[/bold green]")

            # Send a Connection Request Event
            connect_event = ClientConnectionRequestEvent(
                client_type=ClientType.PY_CLIENT,
            )
            await self.websocket.send(connect_event.model_dump_json())
            console.print_json(data=connect_event.model_dump_json(), indent=4)

            # Await Connection Response from Server
            response_message = await self.websocket.recv()
            console.print_json(response_message)
            print(type(response_message))
            try:
                response_event = ConnectionResponseEvent.model_validate_json(response_message)
                self.client_id = response_event.client_id
                # console.print_json(data=response_event.model_dump_json(), indent=4)
                console.print(f"[blue]Assigned Client ID: {
                              self.client_id}[blue]")
            except ValidationError as e:
                console.print(
                    f"[bold red]Failed to validate connection response: {e}[/bold red]")
                await self.websocket.close()
        except Exception as e:
            console.print(f"[bold red]Connection failed: {e}[/bold red]")


    async def send_ping_response(self, target_client_id: str):
        """Send a ping_response event to a target client."""
        if not self.websocket or self.websocket.closed:
            console.print("[bold red]WebSocket is not connected.[/bold red]")
            return

        ping_response_event = PingResponseEvent(
            client_id=self.client_id,
            client_type=ClientType.PY_CLIENT,
            event=EventType.PING_RESPONSE,
            payload={
                "target_client_id": target_client_id,
                "client_type": ClientType.PY_CLIENT,
            },
        )
        await self.websocket.send(ping_response_event.model_dump_json())
        console.print_json(data=ping_response_event.model_dump(), indent=4)

    async def recv(self) -> BaseWebsocketEvent:
        """Receive a message from the server."""
        if not self.websocket or self.websocket.closed:
            console.print("[bold red]WebSocket is not connected.[/bold red]")
            return None

        try:
            message = await self.websocket.recv()
            event = BaseWebsocketEvent.model_validate_json(message)
            return event
        except ValidationError as e:
            console.print(
                f"[bold red]Failed to validate incoming message: {e}[/bold red]")
            return None
        except Exception as e:
            console.print(f"[bold red]Error receiving message: {e}[/bold red]")
            return None

    async def handle_events(self):
        """Handle incoming events from the server."""
        while True:
            event = await self.websocket.recv()
            if event is None:
                continue

            console.print(f"[bold yellow]Received Event: {
                          event.event}[/bold yellow]")
            console.print_json(data=event.model_dump(), indent=4)

            match event.event:
                case EventType.PING:
                    target_client_id = event.payload.target_client_id
                    if target_client_id:
                        delay = random.uniform(0.1, 1.0)
                        console.print(f"[italic]Delaying ping response for {
                                      delay:.2f} seconds...[/italic]")
                        await asyncio.sleep(delay)
                        await self.send_ping_response(target_client_id)

                case _:
                    console.print(f"[bold red]Unknown event type: {
                                  event.event}[/bold red]")


async def handle_client(client: Client):
    await client.connect()
    await client.handle_events()


async def main():
    clients = []
    for _ in range(1):
        client = Client("ws://localhost:8000/ws/py_client")
        clients.append(client)

    # Start all clients concurrently
    await asyncio.gather(*(handle_client(client) for client in clients))

if __name__ == "__main__":
    asyncio.run(main())
