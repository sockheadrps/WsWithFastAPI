from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Union, List, Literal
import uuid

class Connection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    websocket: Any = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow", 
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "websocket": None
                
            }
        }
    )


class WebsocketData(BaseModel):
    data: Dict[str, Union[str, int, bool, List[str], Dict[str, Any]]] = Field(
        ...
    )


class WebsocketEvent(BaseModel):
    event: str
    client_id: str
    data: WebsocketData

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow", 
        from_attributes=True,
        json_schema_extra={
            "example": {
                "event": "ping",
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "data": {}
            }
        }
    )


class PingEvent(WebsocketEvent):
    event: Literal["ping"]
    data: WebsocketData = Field(...)


class PingResponse(WebsocketEvent):
    event: Literal["ping_response"]
    data: WebsocketData
