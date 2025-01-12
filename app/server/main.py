from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict
from app.models.models import WebsocketData, WebsocketEvent, PingEvent, PingResponse, Connection
import uvicorn


app = FastAPI()

app.mount(
    "/static", StaticFiles(directory="server/static"), name="static")

templates = Jinja2Templates(directory="server/templates")


class BaseConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> Connection:
        await websocket.accept()
        connection = Connection(websocket=websocket)
        self.active_connections[connection.id] = websocket
        return connection

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

    async def send_to_client(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    def get_active_connections(self):
        return list(self.active_connections.keys())


class PyConnectionManager(BaseConnectionManager):
    pass

class WebConnectionManager(BaseConnectionManager):
    pass


py_connection_manager = PyConnectionManager()
web_connection_manager = WebConnectionManager()


async def broadcast_py_clients_to_web():
    py_clients = py_connection_manager.get_active_connections()
    for web_client_id in web_connection_manager.active_connections:
        await web_connection_manager.send_to_client(
            web_client_id,
            WebsocketEvent(
                event="py_clients_update",
                client_id=web_client_id,
                data=WebsocketData(data={"py_clients": py_clients})
            ).model_dump()
        )

@app.websocket("/ws/py_client")
async def py_client_websocket_endpoint(websocket: WebSocket):
    connection = await py_connection_manager.connect(websocket)
    await websocket.send_json(WebsocketEvent(
        event="connect",
        client_id=connection.id,
        data=WebsocketData(data={})
    ).model_dump())
    
    # Broadcast updated py clients list to all web clients
    await broadcast_py_clients_to_web()

    try:
        while True:
            message = await websocket.receive_json()
            event = WebsocketEvent.model_validate(message)
            print(event.model_dump())
            if event.event == "ping":
                target_client_id = event.data.data.get("target_client_id")
                if target_client_id:
                    # Send ping response back to web client
                    await web_connection_manager.send_to_client(target_client_id, PingResponse(
                        event="ping_response",
                        client_id=connection.id,
                        data=WebsocketData(data={"target_client_id": target_client_id})
                    ).model_dump())
            elif event.event == "ping_response":
                target_client_id = event.data.data.get("target_client_id")
                if target_client_id:
                    # Send ping response back to web client
                    await web_connection_manager.send_to_client(target_client_id, PingResponse(
                        event="ping_response",
                        client_id=connection.id,
                        data=WebsocketData(data={"target_client_id": target_client_id})
                    ).model_dump())
    except Exception:
        py_connection_manager.disconnect(connection.id)
        await broadcast_py_clients_to_web()


@app.websocket("/ws/web_client")
async def web_client_websocket_endpoint(websocket: WebSocket):
    connection = await web_connection_manager.connect(websocket)
    await websocket.send_json(WebsocketEvent(
        event="connect",
        client_id=connection.id,
        data=WebsocketData(data={})
    ).model_dump())

    # Send current py clients to newly connected web client
    py_clients = py_connection_manager.get_active_connections()
    await websocket.send_json(WebsocketEvent(
        event="py_clients_update",
        client_id=connection.id,
        data=WebsocketData(data={"py_clients": py_clients})
    ).model_dump())

    try:
        while True:
            message = await websocket.receive_json()
            event = WebsocketEvent.model_validate(message)
            print(event.model_dump())
            if event.event == "ping":
                target_client_id = event.data.data.get("target_client_id")
                if target_client_id:
                    # Send ping to target py client
                    await py_connection_manager.send_to_client(target_client_id, PingEvent(
                        event="ping",
                        client_id=connection.id,
                        data=WebsocketData(data={"target_client_id": connection.id})
                    ).model_dump())
    except Exception:
        web_connection_manager.disconnect(connection.id)
        

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ping-schema")
async def ping_schema():
    ping_event_structure = PingEvent.model_json_schema()
    return ping_event_structure


@app.get("/ping-response-schema")
async def ping_response_schema():
    ping_response_structure = PingResponse.model_json_schema()
    return ping_response_structure


if __name__ == "__main__":
    uvicorn.run("server.main:app", host="localhost", port=8000)
