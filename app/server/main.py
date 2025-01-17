from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict
from models.models import WebsocketData, WebsocketEvent, PingEvent, PingResponse, Connection
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
    pass

@app.websocket("/ws/py_client")
async def py_client_websocket_endpoint(websocket: WebSocket):
    connection = await py_connection_manager.connect(websocket)
    await websocket.send_json(WebsocketEvent(event="connect",
                                             client_id=connection.id,
                                             data=WebsocketData(data={})).model_dump())
                                             


@app.websocket("/ws/web_client")
async def web_client_websocket_endpoint(websocket: WebSocket):
    pass
        

@app.get("/")
async def index(request: Request):
    pass


@app.get("/ping-schema")
async def ping_schema() -> JSONResponse:
    ping_event_structure = PingEvent.model_json_schema()
    return JSONResponse(content=ping_event_structure)


@app.get("/ping-response-schema")
async def ping_response_schema():
    ping_response_event_structure = PingResponse.model_json_schema()
    return JSONResponse(content=ping_response_event_structure)


if __name__ == "__main__":
    uvicorn.run("server.main:app", host="localhost", port=8000)
