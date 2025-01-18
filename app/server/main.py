# server/main.py

import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Any, Dict
import uvicorn
from rich.pretty import pprint

from rich import print_json
from rich.console import Console
# Ensure the decorator is correctly imported
from decorators.json_printer import json_printer
from models.models import (
    ConnectionResponsePayload,
    PingPayload,
    ConnectionResponseEvent,
    PingEvent,
    PingResponseEvent,
    ClientType,
    EventType,
    BaseWebsocketEvent,
    Connection
)
from datetime import datetime


def pprint_dump(json_compatible_dict: str) -> None:
    json_compatible_dict = json.loads(json_compatible_dict)
    console.print_json(data=json_compatible_dict, indent=4)


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="server/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="server/templates")

# Initialize Rich Console
console = Console()

# Define Connection Managers


class BaseConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> Connection:
        await websocket.accept()
        connection = Connection(websocket=websocket)
        pprint_dump(connection.model_dump_json())
        self.active_connections[str(connection.client_id)] = websocket

        # Create a connection response payload
        connection_response_payload = ConnectionResponsePayload(
            client_id=connection.client_id,
            client_type=ClientType.SERVER,
            server_time=datetime.now()
        )

        pprint_dump(connection_response_payload.model_dump_json())

        return connection, connection_response_payload

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        console.print_json(
            data={
                "action": "disconnect",
                "client_id": str(client_id),
                "timestamp": str(datetime.now()),
            },
            indent=4,
        )

    async def send_to_client(self, client_id: str, event: BaseWebsocketEvent):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_json(event.model_dump())
            pprint_dump(event.model_dump_json())

    def get_active_connections(self) -> list:
        return list(self.active_connections.keys())

    def get_client_type(self) -> str:
        raise NotImplementedError("Must implement in subclass.")


class PyConnectionManager(BaseConnectionManager):
    def get_client_type(self) -> str:
        return ClientType.PY_CLIENT.value


class WebConnectionManager(BaseConnectionManager):
    def get_client_type(self) -> str:
        return ClientType.WEB_CLIENT.value


# Instantiate connection managers
py_connection_manager = PyConnectionManager()
web_connection_manager = WebConnectionManager()


async def broadcast_py_clients_to_web():
    py_clients = py_connection_manager.get_active_connections()
    # event = BaseWebsocketEvent(
    #     client_id="server",
    #     client_type=ClientType.SERVER,
    #     event=EventType.PING,
    #     payload={
    #         "py_clients": py_clients
    #     },  # Assuming payload can accept a dict directly
    # )
    # for web_client_id in web_connection_manager.get_active_connections():
    #     await web_connection_manager.send_to_client(web_client_id, event)


@app.websocket("/ws/py_client")
async def py_websocket_endpoint(websocket: WebSocket):
    try:
        # Connect and obtain client_id
        client, connection_response_payload = await py_connection_manager.connect(websocket)

        # Send connection event to py_client
        connection_event = ConnectionResponseEvent(
            client_id=ClientType.SERVER,
            client_type=ClientType.SERVER,
            event=EventType.CONNECTION_RESPONSE,
            payload=connection_response_payload,
        )
        await websocket.send_text(connection_event.model_dump_json())
        pprint_dump(connection_event.model_dump_json())

        # Broadcast updated py clients to all web clients
        await broadcast_py_clients_to_web()

        while True:
            message = await websocket.receive_json()
            event = BaseWebsocketEvent.model_validate(message)

            if event.event == EventType.PING and event.payload:
                if isinstance(event.payload, PingPayload):
                    target_client_id = event.payload.target_client_id
                    ping_response_event = PingResponseEvent(
                        client_id=event.client_id,
                        client_type=ClientType.PY_CLIENT,
                        event=EventType.PING_RESPONSE,
                        payload=PingPayload(
                            target_client_id=event.target_client_id,
                            client_type=ClientType.SERVER,
                        ),
                    )
                    await web_connection_manager.send_to_client(
                        target_client_id, ping_response_event
                    )

            elif event.event == EventType.PING_RESPONSE and event.payload:
                if isinstance(event.payload, PingPayload):
                    target_client_id = event.payload.target_client_id
                    ping_response_event = PingResponseEvent(
                        client_id=event.client_id,
                        client_type=ClientType.PY_CLIENT,
                        event=EventType.PING_RESPONSE,
                        payload=PingPayload(
                            target_client_id=target_client_id,
                            client_type=ClientType.SERVER,
                        ),
                    )
                    await web_connection_manager.send_to_client(
                        target_client_id, ping_response_event
                    )
            elif event.event == EventType.CONNECT:
                pass

            else:
                console.print_json(
                    data={
                        "action": "unknown_event",
                        "client_id": event.client_id,
                        "event": event.event,
                        "data": event.payload,
                    },
                    indent=4,
                )

    except WebSocketDisconnect:
        py_connection_manager.disconnect(client.client_id)
        await broadcast_py_clients_to_web()


@app.websocket("/ws/web_client")
async def web_websocket_endpoint(websocket: WebSocket) -> None:
    try:
        # Connect and obtain client_id
        client_id = await web_connection_manager.connect(websocket)

        # Send connection event to web_client
        connection_event = ConnectionResponseEvent(
            client_id=client_id,
            client_type=ClientType.WEB_CLIENT,
            event=EventType.CONNECT,
            payload=ConnectionResponsePayload(
                client_id=client_id,
                client_type=ClientType.SERVER,
                server_time=datetime.now(),
            ),
        )
        await websocket.send_json(connection_event.model_dump())
        console.print_json(data=connection_event.model_dump(), indent=4)

        # Send current py clients to newly connected web client
        py_clients = py_connection_manager.get_active_connections()
        py_clients_update_event = BaseWebsocketEvent(
            client_id=client_id,
            client_type=ClientType.SERVER,
            event=EventType.PING,
            payload={"py_clients": py_clients},
        )
        await websocket.send_json(py_clients_update_event.model_dump())
        console.print_json(data=py_clients_update_event.model_dump(), indent=4)

        while True:
            message = await websocket.receive_json()
            event = BaseWebsocketEvent.model_validate(message)

            if event.event == EventType.PING and event.payload:
                if isinstance(event.payload, PingPayload):
                    target_client_id = event.payload.target_client_id
                    ping_event = PingEvent(
                        client_id=client_id,
                        client_type=ClientType.WEB_CLIENT,
                        event=EventType.PING,
                        payload=PingPayload(
                            target_client_id=target_client_id,
                            client_type=ClientType.WEB_CLIENT,
                        ),
                    )
                    await py_connection_manager.send_to_client(
                        target_client_id, ping_event
                    )

            elif event.event == EventType.PING_RESPONSE and event.payload:
                if isinstance(event.payload, PingPayload):
                    target_client_id = event.payload.target_client_id
                    ping_response_event = PingResponseEvent(
                        client_id=client_id,
                        client_type=ClientType.WEB_CLIENT,
                        event=EventType.PING_RESPONSE,
                        payload=PingPayload(
                            target_client_id=target_client_id,
                            client_type=ClientType.SERVER,
                        ),
                    )
                    await py_connection_manager.send_to_client(
                        target_client_id, ping_response_event
                    )

            else:
                console.print_json(
                    data={
                        "action": "unknown_event",
                        "client_id": client_id,
                        "event": event.event,
                        "data": event.payload,
                        "timestamp": datetime.now(),
                    },
                    indent=4,
                )

    except WebSocketDisconnect:
        web_connection_manager.disconnect(client_id)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ping-schema")
async def ping_schema():
    ping_event_structure = PingEvent.model_json_schema()
    return ping_event_structure


@app.get("/ping-response-schema")
async def ping_response_schema():
    ping_response_structure = PingResponseEvent.model_json_schema()
    return ping_response_structure


if __name__ == "__main__":
    uvicorn.run("server.main:app", host="localhost", port=8000)
