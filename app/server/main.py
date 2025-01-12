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
        pass

    async def connect(self, websocket: WebSocket) -> Connection:
        pass

    def disconnect(self, connection_id: str):
        pass

    async def send_to_client(self, client_id: str, message: dict):
        pass

    def get_active_connections(self):
        pass


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
    pass


@app.websocket("/ws/web_client")
async def web_client_websocket_endpoint(websocket: WebSocket):
    pass
        

@app.get("/")
async def index(request: Request):
    pass


@app.get("/ping-schema")
async def ping_schema():
    pass


@app.get("/ping-response-schema")
async def ping_response_schema():
    pass


if __name__ == "__main__":
    uvicorn.run("server.main:app", host="localhost", port=8000)
