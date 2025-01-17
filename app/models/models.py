from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Union, List, Literal
import uuid
from fastapi import WebSocket


class Connection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    websocket: WebSocket

    class Config:
        arbitrary_types_allowed = True


class WebsocketData(BaseModel):
    data: Dict[str, Union[str, int, bool, List[str], Dict[str, Any]]] = Field(...)


class WebsocketEvent(BaseModel):
    event: str
    client_id: str
    data: WebsocketData

class PingEvent(WebsocketEvent):
    event: Literal["ping"]
    data: WebsocketData = Field(...)


class PingResponse(WebsocketEvent):
    event: Literal["ping_response"]
    data: WebsocketData
