import json
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any
from fastapi import WebSocket
from enum import Enum
import uuid
from uuid import UUID
from datetime import datetime
from server.utilities.stats import Computer


class Connection(BaseModel):
    client_id: UUID = Field(default_factory=uuid.uuid4)
    websocket: WebSocket

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            WebSocket: lambda ws: repr(ws),
            UUID: lambda x: str(x),
            datetime: lambda dt: dt.isoformat(),
        },
    )


class EventType(str, Enum):
    DATA_REQUEST = "data-request"


class ConnectionResponsePayload(BaseModel):
    client_id: UUID
    server_time: datetime


class BaseWebsocketEvent(BaseModel):
    client_id: UUID = Field(default_factory=uuid.uuid4)
    event: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class StatsPayload(BaseModel):
    cpu_count: int
    cpu_usage: float
    cpu_frequency: Dict[str, float]
    core_temperatures: Dict[str, float]
    ram_total: float
    ram_available: float
    ram_percentage: float
    disk_total: float
    disk_free: float
    disk_used: float
    disk_percentage: float


class StatsEvent(BaseModel):
    client_id: UUID | str
    event: str
    data: StatsPayload = Field(default_factory=lambda: StatsPayload(**Computer.get_stats_dict()))
    timestamp: datetime = Field(default_factory=datetime.now)

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["client_id"] = str(data["client_id"])
        data["timestamp"] = data["timestamp"].isoformat()
        return data
