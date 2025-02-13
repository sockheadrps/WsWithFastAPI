import signal
import sys
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from server.utilities.models.models import StatsEventPayload
from .utilities.manager import Manager
from rich.pretty import pprint

app = FastAPI(
    title="Server Statistics Dashboard",
    description="Real-time server metrics visualization",
    version="1.0.0",
)

API_VERSION = app.version  # Extract the version for reuse

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")
connection_manager = Manager()


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.get("/favicon.ico")
async def favicon() -> None:
    raise HTTPException(status_code=404, detail="Favicon not implemented")


@app.get("/stats", response_class=HTMLResponse)
async def stats_endpoint(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket(f"/api/{API_VERSION}/ws/stats")
async def stats_websocket(client_websocket: WebSocket):
    try:
        connection = await connection_manager.connect(client_websocket)
        pprint(connection)
        await connection_manager.handle_message(connection)
    except WebSocketDisconnect:
        await connection_manager.disconnect(str(connection.model_dump()["clien_id"]))


@app.get(f"/api/{API_VERSION}/data-schema")
def data_schema():
    return {"data_schema": StatsEventPayload.model_json_schema()}


if __name__ == "__main__":
    try:
        uvicorn.run("server.main:app", host="localhost", port=8000)
    except KeyboardInterrupt:
        signal_handler(None, None)
