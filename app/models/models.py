from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Any, Dict, Union, List, Literal, Optional
from fastapi import WebSocket
from datetime import datetime, timezone
from enum import Enum
import uuid
from uuid import UUID


class Connection(BaseModel):
    client_id: UUID = Field(default_factory=uuid.uuid4)
    websocket: WebSocket

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            WebSocket: lambda ws: repr(ws),
            UUID: lambda id: str(id),
            datetime: lambda dt: dt.isoformat()

        }
    )


class EventType(str, Enum):
    PING = "ping"
    PING_RESPONSE = "ping_response"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    CONNECTION_RESPONSE = "connection_response"


class ClientType(str, Enum):
    PY_CLIENT = "py_client"
    SERVER = "server"
    WEB_CLIENT = "web_client"


class WebsocketPayload(BaseModel):
    content: Dict[str, Union[str, int, bool, List[str], Dict[str, Any]]]


class PingPayload(BaseModel):
    target_client_id: Union[UUID, int, str]
    client_type: ClientType


class ConnectionResponsePayload(BaseModel):
    client_id: Union[UUID, int, str]
    client_type: ClientType = ClientType.SERVER
    server_time: datetime = Field(default_factory=lambda: datetime.now())

    model_config = ConfigDict(
        json_encoders={
            UUID: lambda id: str(id),
            datetime: lambda dt: dt.isoformat()
        }
    )


class BaseWebsocketEvent(BaseModel):
    client_id: Union[UUID, int, str] = Field(default_factory=uuid.uuid4)
    client_type: ClientType
    event: EventType
    payload: Optional[Union["ConnectionResponsePayload",
                            "PingPayload"]] = None

    @model_validator(mode="before")
    def check_event_and_payload(cls, values):
        event = values.get("event")
        payload = values.get("payload")
        client_type = values.get("client_type")

        if event == EventType.PING:
            valid_senders = {ClientType.WEB_CLIENT, ClientType.SERVER}
            if client_type not in valid_senders:
                raise ValueError(
                    "'ping' event must be from server or web_client")
            if not isinstance(payload, PingPayload):
                raise ValueError("'ping' event requires a PingPayload.")
            if not payload.target_client_id:
                raise ValueError(
                    "'ping' event requires 'target_client_id' in payload")

        return values
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        ser_json_typed=True,
        json_encoders={
            WebSocket: lambda ws: repr(ws),
            UUID: lambda id: str(id),
            datetime: lambda dt: dt.isoformat()
        }
    )

    def model_dump(self, **kwargs):
        return super().model_dump(exclude_unset=True, mode="export", **kwargs)  # Default mode


class ConnectionResponseEvent(BaseWebsocketEvent):
    event: Literal[EventType.CONNECTION_RESPONSE] = Field(
        default=EventType.CONNECTION_RESPONSE)
    payload: Union[ConnectionResponsePayload, None] = None
    client_type: Literal[ClientType.SERVER] = Field(default=ClientType.SERVER)

    model_config = ConfigDict(
        json_encoders={
            UUID: lambda id: str(id),
            datetime: lambda dt: str(dt),
        }
    )

    @model_validator(mode="before")
    def uuid_to_str(cls, values):
        if isinstance(values.get("client_id"), UUID):
            values["client_id"] = str(values["client_id"])
        return values


class ClientConnectionRequestEvent(BaseWebsocketEvent):
    event: Literal[EventType.CONNECT] = Field(
        default=EventType.CONNECT)
    client_type: Literal[ClientType.PY_CLIENT] = Field(
        default=ClientType.PY_CLIENT)

    model_config = ConfigDict(
        json_encoders={
            UUID: lambda id: str(id),
            datetime: lambda dt: str(dt),
        }
    )


class PingEvent(BaseWebsocketEvent):
    event: Literal[EventType.PING] = Field(default=EventType.PING)
    payload: PingPayload


class PingResponseEvent(BaseWebsocketEvent):
    event: Literal[EventType.PING_RESPONSE] = Field(
        default=EventType.PING_RESPONSE)
    client_type: Literal[ClientType.SERVER, ClientType.PY_CLIENT]
    payload: PingPayload


BaseWebsocketEvent.model_rebuild()
