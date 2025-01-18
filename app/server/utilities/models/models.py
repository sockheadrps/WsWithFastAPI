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
    pass


class EventType(str, Enum):
    pass


class ConnectionResponsePayload(BaseModel):
    pass


class BaseWebsocketEvent(BaseModel):
    pass


class StatsPayload(BaseModel):
    pass


class StatsEvent(BaseModel):
    pass
