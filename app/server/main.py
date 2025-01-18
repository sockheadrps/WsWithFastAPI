import signal
import sys
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from rich.console import Console
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
console = Console()
connection_manager = Manager()


def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT"""
    console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.get("/favicon.ico")
async def favicon() -> None:
    """Temporary favicon endpoint"""
    raise HTTPException(status_code=404, detail="Favicon not implemented")


@app.get("/stats", response_class=HTMLResponse)
async def stats_endpoint(request: Request) -> HTMLResponse:
    """Serve the statistics dashboard HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket(f"/api/{API_VERSION}/ws/stats")
async def stats_websocket(client_websocket: WebSocket):
    """
    WebSocket endpoint for real-time server statistics.
    Handles client connections and broadcasts system metrics.
    """
    try:
        connection = await connection_manager.connect(client_websocket)
        await connection_manager.handle_message(connection)

    except Exception as e:
        console.print(f"[red]WebSocket connection error: {str(e)}[/red]")

    finally:
        await connection_manager.disconnect(str(connection.client_id))


@app.get(f"/api/{API_VERSION}/data-schema")
def data_schema():
    """Return the JSON schema for stats payload validation"""
    return {"data_schema": StatsPayload.model_json_schema()}


if __name__ == "__main__":
    try:
        uvicorn.run("server.main:app", host="localhost", port=8000)
    except KeyboardInterrupt:
        signal_handler(None, None)
