from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    UUID4,
    InstanceOf,
    AliasGenerator,
)
from pydantic.alias_generators import to_camel
from typing import Dict
from fastapi import WebSocket
from enum import Enum
import uuid
from datetime import datetime
from server.utilities.stats import Computer


class Connection(BaseModel):
    client_id: UUID4 = Field(default_factory=uuid.uuid4)
    websocket: InstanceOf[WebSocket]

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)


class EventType(str, Enum):
    CONNECT = "CONNECT"
    CONNECTION_RESPONSE = "CONNECTION_RESPONSE"
    DATA_REQUEST = "DATA-REQUEST"


class ConnectionResponsePayload(BaseModel):
    client_id: InstanceOf[UUID4]

    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel), frozen=True)


class BaseWebsocketEvent(BaseModel):
    event: InstanceOf[EventType]
    data: InstanceOf[ConnectionResponsePayload]
    time: InstanceOf[datetime] = Field(default_factory=datetime.now)

    model_config = ConfigDict(use_enum_values=True, frozen=True)


class StatsData(BaseModel):
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


class StatsEventPayload(BaseModel):
    event: InstanceOf[EventType]
    data: StatsData = Field(default_factory=lambda: StatsData(**Computer.get_stats_dict()))
