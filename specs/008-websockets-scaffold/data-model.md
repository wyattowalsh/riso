# Data Model: WebSocket Scaffold

**Feature**: 008-websockets-scaffold | **Date**: 2025-11-01  
**Phase**: 1 (Design & Contracts) | **Status**: Complete

## Overview

This document defines the core data structures for WebSocket communication, connection management, and broadcasting. All models use Pydantic for validation and FastAPI for serialization.

## Core Entities

### 1. WebSocketConnection

Represents an active WebSocket connection with lifecycle management.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `connection_id` | `str` | Unique connection identifier | UUID4 format, immutable |
| `websocket` | `WebSocket` | FastAPI WebSocket instance | Required, managed by framework |
| `user` | `Optional[User]` | Authenticated user object | None for anonymous connections |
| `connected_at` | `datetime` | Connection establishment time | UTC timezone, auto-generated |
| `last_activity_at` | `datetime` | Last message send/receive time | Updated on each message |
| `metadata` | `Dict[str, Any]` | Custom connection attributes | User agent, IP, custom tags |
| `rooms` | `Set[str]` | Room IDs this connection belongs to | Mutable set |
| `message_queue` | `asyncio.Queue` | Outbound message buffer | Bounded by `queue_depth` config |
| `state` | `ConnectionState` | Current connection state | Enum: CONNECTING, CONNECTED, CLOSING, CLOSED |

**Methods**:

- `async send_json(message: dict)` - Queue JSON message for sending
- `async send_text(text: str)` - Queue text message
- `async send_bytes(data: bytes)` - Queue binary message
- `async close(code: int, reason: str)` - Gracefully close connection
- `async join_room(room_id: str)` - Add connection to room
- `async leave_room(room_id: str)` - Remove connection from room
- `is_active() -> bool` - Check if connection is active
- `time_since_activity() -> float` - Seconds since last activity

**State Transitions**:

```text
CONNECTING -> CONNECTED (after websocket.accept())
CONNECTED -> CLOSING (on close initiated)
CLOSING -> CLOSED (after cleanup)
```

**Validation Rules**:

- `connection_id` must be valid UUID4
- `connected_at` cannot be in future
- `last_activity_at` >= `connected_at`
- `state` transitions must follow valid paths

**Pydantic Model**:

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, Set
from enum import Enum
import uuid

class ConnectionState(str, Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CLOSING = "closing"
    CLOSED = "closed"

class WebSocketConnectionModel(BaseModel):
    """Serializable connection metadata (excludes WebSocket instance)."""
    connection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    rooms: Set[str] = Field(default_factory=set)
    state: ConnectionState = ConnectionState.CONNECTING
    
    @validator("last_activity_at")
    def activity_after_connection(cls, v, values):
        if "connected_at" in values and v < values["connected_at"]:
            raise ValueError("last_activity_at cannot be before connected_at")
        return v
    
    class Config:
        use_enum_values = True
```

### 2. Message

Data structure for WebSocket messages with routing and metadata.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `message_id` | `str` | Unique message identifier | UUID4 format |
| `type` | `str` | Message type discriminator | Required, max 50 chars |
| `payload` | `Dict[str, Any]` | Message content | JSON-serializable |
| `sender_id` | `str` | Connection ID of sender | Must be valid connection |
| `room_id` | `Optional[str]` | Target room (for broadcasts) | None for direct messages |
| `timestamp` | `datetime` | Message creation time | UTC timezone |
| `correlation_id` | `Optional[str]` | Request-response correlation | UUID4 format |
| `metadata` | `Dict[str, Any]` | Custom message attributes | Headers, priority, etc. |

**Message Types** (extensible):

- `connection.connect` - Connection established
- `connection.disconnect` - Connection closed
- `message.text` - Text message
- `message.json` - JSON data
- `message.binary` - Binary data
- `room.join` - Join room request
- `room.leave` - Leave room request
- `room.broadcast` - Broadcast to room
- `error` - Error response

**Validation Rules**:

- `message_id` must be valid UUID4
- `type` must match pattern `^[a-z0-9._-]+$`
- `payload` must be JSON-serializable (no circular refs)
- `timestamp` cannot be in future
- `correlation_id` (if present) must be valid UUID4

**Pydantic Model**:

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import re

class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(..., min_length=1, max_length=50)
    payload: Dict[str, Any]
    sender_id: str
    room_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("type")
    def validate_type_format(cls, v):
        if not re.match(r"^[a-z0-9._-]+$", v):
            raise ValueError("type must contain only lowercase alphanumeric, dots, dashes, underscores")
        return v
    
    @validator("timestamp")
    def timestamp_not_future(cls, v):
        if v > datetime.utcnow():
            raise ValueError("timestamp cannot be in future")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### 3. Room

Logical grouping of connections for targeted broadcasting.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `room_id` | `str` | Unique room identifier | Max 100 chars, URL-safe |
| `name` | `Optional[str]` | Human-readable room name | Max 200 chars |
| `created_at` | `datetime` | Room creation time | UTC timezone |
| `connection_ids` | `Set[str]` | Set of connection IDs in room | Dynamically managed |
| `metadata` | `Dict[str, Any]` | Custom room attributes | Permissions, type, etc. |
| `max_connections` | `Optional[int]` | Connection limit | None = unlimited |
| `is_private` | `bool` | Requires authorization | Default False |

**Operations**:

- `add_connection(connection_id: str)` - Add connection to room
- `remove_connection(connection_id: str)` - Remove connection
- `get_connection_count() -> int` - Current member count
- `is_full() -> bool` - Check if room at capacity
- `can_join(user: User) -> bool` - Check join permissions

**Validation Rules**:

- `room_id` must be URL-safe (alphanumeric + dashes/underscores)
- `connection_ids` must reference valid connections
- `max_connections` must be positive if set
- Room cannot exceed `max_connections` capacity

**Pydantic Model**:

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, Set
import re

class Room(BaseModel):
    room_id: str = Field(..., min_length=1, max_length=100)
    name: Optional[str] = Field(None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    connection_ids: Set[str] = Field(default_factory=set)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    max_connections: Optional[int] = Field(None, gt=0)
    is_private: bool = False
    
    @validator("room_id")
    def validate_room_id_format(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("room_id must be URL-safe (alphanumeric, dashes, underscores)")
        return v
    
    def is_full(self) -> bool:
        if self.max_connections is None:
            return False
        return len(self.connection_ids) >= self.max_connections
    
    def get_connection_count(self) -> int:
        return len(self.connection_ids)
```

### 4. ConnectionMetadata

Extended metadata for connection tracking and monitoring.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `ip_address` | `str` | Client IP address | IPv4/IPv6 format |
| `user_agent` | `Optional[str]` | Client user agent string | Max 500 chars |
| `platform` | `Optional[str]` | Client platform | mobile/desktop/bot |
| `session_id` | `Optional[str]` | Browser session ID | For multi-tab tracking |
| `referrer` | `Optional[str]` | Connection origin | URL format |
| `custom` | `Dict[str, Any]` | Application-specific metadata | JSON-serializable |

**Validation Rules**:

- `ip_address` must be valid IPv4 or IPv6
- `user_agent` max 500 characters (prevent header injection)
- `referrer` must be valid URL if present

**Pydantic Model**:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import ipaddress

class ConnectionMetadata(BaseModel):
    ip_address: str
    user_agent: Optional[str] = Field(None, max_length=500)
    platform: Optional[str] = Field(None, pattern="^(mobile|desktop|bot)$")
    session_id: Optional[str] = None
    referrer: Optional[str] = None
    custom: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("ip_address")
    def validate_ip_address(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("ip_address must be valid IPv4 or IPv6")
        return v
```

### 5. ConnectionMiddleware

Interceptor pattern for cross-cutting concerns.

**Interface**:

```python
from abc import ABC, abstractmethod
from typing import Optional

class ConnectionMiddleware(ABC):
    """Base class for WebSocket middleware."""
    
    @abstractmethod
    async def on_connect(
        self,
        connection: WebSocketConnection,
        request: Request
    ) -> Optional[dict]:
        """Called when connection is established. Return metadata or None."""
        pass
    
    @abstractmethod
    async def on_disconnect(
        self,
        connection: WebSocketConnection,
        code: int,
        reason: str
    ):
        """Called when connection closes."""
        pass
    
    @abstractmethod
    async def on_message(
        self,
        connection: WebSocketConnection,
        message: Message
    ) -> Message:
        """Called on incoming message. Can modify or reject message."""
        pass
    
    @abstractmethod
    async def on_error(
        self,
        connection: WebSocketConnection,
        error: Exception
    ):
        """Called on error. Log, alert, or handle gracefully."""
        pass
```

**Built-in Middlewares**:

- `AuthenticationMiddleware` - Validates JWT tokens, attaches user
- `LoggingMiddleware` - Structured logging with correlation IDs
- `MetricsMiddleware` - Prometheus metrics collection
- `RateLimitMiddleware` - Message rate limiting per connection
- `ValidationMiddleware` - Pydantic schema validation

## Entity Relationships

```text
ConnectionManager (Singleton)
├─ connections: Dict[str, WebSocketConnection]  # All active connections
├─ rooms: Dict[str, Room]                       # All active rooms
└─ middlewares: List[ConnectionMiddleware]      # Global middleware chain

WebSocketConnection
├─ user: Optional[User]                         # From auth (spec 009)
├─ rooms: Set[str]                              # Room membership
├─ metadata: ConnectionMetadata                 # Extended tracking
└─ message_queue: asyncio.Queue[Message]        # Outbound buffer

Room
├─ connection_ids: Set[str]                     # Members (references WebSocketConnection)
└─ metadata: Dict[str, Any]                     # Room-specific data

Message
├─ sender_id: str                               # References WebSocketConnection
└─ room_id: Optional[str]                       # References Room
```

## Database Schema (Optional - Not Included by Default)

If users enable database integration (spec 008), they may persist:

### `websocket_message_history` Table

```sql
CREATE TABLE websocket_message_history (
    message_id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    sender_id UUID NOT NULL,
    room_id VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL,
    correlation_id UUID,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_message_room_timestamp ON websocket_message_history(room_id, timestamp DESC);
CREATE INDEX idx_message_sender ON websocket_message_history(sender_id);
```

### `websocket_room_metadata` Table

```sql
CREATE TABLE websocket_room_metadata (
    room_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    max_connections INTEGER,
    is_private BOOLEAN DEFAULT FALSE
);
```

**Note**: Database persistence is **out of scope** for this feature (constitution: minimal baseline). Patterns documented in `docs/modules/websockets.md` for users who need history.

## Configuration Model

```python
from pydantic_settings import BaseSettings

class WebSocketConfig(BaseSettings):
    """WebSocket configuration with environment variable support."""
    
    # Connection limits
    max_connections_global: int = 10000
    max_connections_per_user: int = 5
    max_connections_per_ip: int = 100
    
    # Timeouts (seconds)
    heartbeat_interval: int = 30
    heartbeat_timeout: int = 60
    idle_timeout: int = 300  # 5 minutes
    
    # Message handling
    max_message_size: int = 1024 * 1024  # 1MB
    message_queue_depth: int = 100
    
    # Broadcasting
    broadcast_timeout: float = 5.0
    broadcast_chunk_size: int = 1000  # Max connections per parallel batch
    
    # Rate limiting
    rate_limit_messages: int = 100  # Max messages per window
    rate_limit_window: int = 60  # Window in seconds
    
    class Config:
        env_prefix = "WS_"
        case_sensitive = False
```

## Type Definitions

```python
from typing import TypedDict, Literal

# Message type hints
MessageType = Literal[
    "connection.connect",
    "connection.disconnect",
    "message.text",
    "message.json",
    "message.binary",
    "room.join",
    "room.leave",
    "room.broadcast",
    "error"
]

# Error codes
class ErrorCode:
    AUTHENTICATION_REQUIRED = "AUTH_REQUIRED"
    AUTHENTICATION_FAILED = "AUTH_FAILED"
    AUTHORIZATION_FAILED = "AUTHZ_FAILED"
    MESSAGE_TOO_LARGE = "MESSAGE_TOO_LARGE"
    QUEUE_FULL = "BACKPRESSURE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT"
    INVALID_MESSAGE_FORMAT = "INVALID_FORMAT"
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    ROOM_FULL = "ROOM_FULL"
    INTERNAL_ERROR = "INTERNAL_ERROR"

# Connection close codes (WebSocket protocol)
class CloseCode:
    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    INTERNAL_ERROR = 1011
```

## Summary

This data model provides:

- **Type Safety**: Pydantic validation for all entities
- **Flexibility**: Extensible metadata fields
- **Performance**: In-memory structures optimized for lookups
- **Monitoring**: Timestamps and state tracking built-in
- **Security**: Validation rules prevent injection and abuse

All models follow Python 3.11+ type hints and FastAPI conventions for seamless integration with existing FastAPI scaffold (spec 006).
