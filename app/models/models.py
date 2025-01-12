from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Union, List, Literal
import uuid
from fastapi import WebSocket


class Connection(BaseModel):
    pass


class WebsocketData(BaseModel):
    pass


class WebsocketEvent(BaseModel):
    pass

class PingEvent(WebsocketEvent):
    pass


class PingResponse(WebsocketEvent):
    pass
