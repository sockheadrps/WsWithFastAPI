import signal
import sys
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from server.utilities.models.models import StatsPayload
from .utilities.manager import Manager

app = FastAPI(
    title="Server Statistics Dashboard", 
    description="Real-time server metrics visualization", 
    version="1.0.0"
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
    pass


@app.websocket(f"/api/{API_VERSION}/ws/stats")
async def stats_websocket(client_websocket: WebSocket):
    pass


@app.get(f"/api/{API_VERSION}/data-schema")
def data_schema():
    pass


if __name__ == "__main__":
    try:
        uvicorn.run("server.main:app", host="localhost", port=8000)
    except KeyboardInterrupt:
        signal_handler(None, None)