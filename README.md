
# Project Setup
Create a python virtual environment.
```bash
python -m venv .venv
```

Activate the virtual environment.
linux:
```bash
source .venv/bin/activate
``` 
windows:
```bash
.venv\Scripts\activate
```

Create a directory, `py_websockets`, and inside it, three more directories: `client`, `server`, and `models`.
Each of these directories will have a `__init__.py` file, including the root directory. In both the `client` and `server` directories, create a `main.py`. The models directory will get a `models.py`, and also the server directory will get `templates` and `static` directories.
The file structure should look like this:
```
py_websockets/
    __init__.py
    client/
        __init__.py
        main.py
    server/
        templates/
        static/ 
        __init__.py
        main.py
```

## 1. Introduction to FastAPI WebSockets

**Overview:**  
FastAPI provides a simple way to create WebSocket endpoints that enable real-time communication between clients and the server. WebSocket connections are long-lived, meaning they stay open until explicitly closed. This allows for bidirectional communication between clients and the server without the need to repeatedly establish new HTTP requests.

## 2. Setting Up the FastAPI App

Now, let's create a basic FastAPI application. We'll start by setting up the server and configuring static file and template handling.

```python
import uuid
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Literal
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Serve static files (optional, for assets like CSS, JS)
app.mount(
    "/static", StaticFiles(directory="static"), name="static"
)

# Set up templates for rendering HTML pages
templates = Jinja2Templates(directory="templates")
```


**Explanation:**

- `app.mount()`: This mounts static files, making them available at the `/static` path. Static files might include things like CSS, images, or JavaScript files that the client needs.
  
- `templates`: This initializes the Jinja2 template engine, which allows us to render dynamic HTML templates. By specifying the `templates` directory, we can serve HTML files to the client dynamically.

Next, we will go over how to handle WebSocket connections.



## 3. Define WebSocket Data Structures

In this section, we will introduce Pydantic models to structure and validate the data passed through WebSocket messages. These models will help ensure the messages are properly formatted and the data is validated before it's processed.

We'll create a `WebsocketEvent` model that represents the events sent over WebSocket

```python
class WebsocketData(BaseModel):
    data: Dict[str, Any]

class WebsocketEvent(BaseModel):
    event: str
    client_id: str
    data: WebsocketData
```


# Creating the WebSocket Connection Manager

The `BaseConnectionManager` class is responsible for maintaining a dictionary of active WebSocket connections. It allows the server to:

- Accept and manage incoming WebSocket connections.
- Disconnect clients when they leave.
- Send messages to specific clients using their unique connection IDs.

## 1.1 Defining the Connection Manager
To begin, we define the `BaseConnectionManager` class. This class will use a dictionary to store active WebSocket connections.

Inside the class, we'll define methods for managing connections: accepting incoming WebSocket connections, generating unique IDs, and storing the connections. We also need to send an initial "connect" event to the client when the connection is established.

The `connect` method will:

1. Accept the incoming WebSocket connection.
2. Generate a unique connection ID.
3. Store the connection in the `active_connections` dictionary.
4. Send a "connect" event back to the client.



```python
class BaseConnectionManager:
    def __init__(self):
        # Active connections dictionary (client_id -> WebSocket)
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        # Accept the incoming WebSocket connection
        await websocket.accept()

        # Generate a unique ID for the new connection
        connection_id = str(uuid.uuid4())  # Generate a unique ID for each connection

        # Store the connection in the active_connections dictionary
        self.active_connections[connection_id] = websocket

        # Print out that the client has connected
        print(f"Client {connection_id} connected")

        # Send a simple "connect" event to the client when they connect
        connect_event = WebsocketEvent(
            event="connect",
            client_id=connection_id,
            data=WebsocketData(data={"message": "connection request granted"})
        )
        # Send the event as a JSON message to the client
        await websocket.send_json(connect_event.model_dump())

        # Return the generated connection ID
        return connection_id
```


## 1.2 Disconnecting Clients
The `disconnect` method is used to remove a client from the active connections list when they disconnect.

This method:

1. Takes the `connection_id` as an argument.
2. Checks if the client exists in the `active_connections` dictionary.
3. If the client exists, removes them from the dictionary.

```python
    async def disconnect(self, connection_id: str) -> None:
        # Check if the client ID exists in the active connections dictionary
        if connection_id in self.active_connections:
            # Remove the connection from the active_connections dictionary
            del self.active_connections[connection_id]
```

## 1.3 Sending Messages to Clients
The `send_to_client` method allows the server to send messages to specific clients by their unique connection ID.

This method:

1. Takes a `client_id` and a `message` as arguments.
2. Checks if the `client_id` exists in the `active_connections` dictionary.
3. If the client exists, sends the provided message to that client.

```python
    async def send_to_client(self, client_id: str, message: dict) -> None:
        # Check if the client ID exists in the active connections
        if client_id in self.active_connections:
            # Send the message as a JSON object to the client
            await self.active_connections[client_id].send_json(message)

```

# How to Use the BaseConnectionManager

The `BaseConnectionManager` can be used to manage WebSocket connections in the FastAPI application. Here's how it will fit into the WebSocket endpoint:

- The manager will accept new connections and assign them a unique ID.
- It will allow the server to send messages to specific clients based on their connection ID.
- It will manage the disconnection process when clients leave.

```python
# Create an instance of BaseConnectionManager to manage WebSocket connections
py_connection_manager = BaseConnectionManager()

@app.websocket("/ws/py_client")
async def websocket_endpoint(websocket: WebSocket):
    # Accept and manage the WebSocket connection
    connection_id = await py_connection_manager.connect(websocket)
    
    # Handle incoming messages and events
    try:
        while True:
            message = await websocket.receive_json()
            event = WebsocketEvent(**message)
            print(f"Received event: {event.event}")
            # Handle the event logic here...

    except WebSocketDisconnect:
        # Handle the client disconnection
        print(f"Client {connection_id} disconnected")
        await py_connection_manager.disconnect(connection_id)

    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        await py_connection_manager.disconnect(connection_id)
```


## 2. Setting Up the WebSocket Endpoint
Now that we have the connection manager set up, let's implement a WebSocket endpoint. This endpoint will accept incoming WebSocket connections, manage them using the `BaseConnectionManager`, and handle simple events like "connect".

The WebSocket endpoint will:

1. Accept incoming connections using the `BaseConnectionManager`.
2. Send a "connect" event when a client connects.
3. Listen for incoming events and handle them accordingly.

```python
# Create an instance of BaseConnectionManager to manage WebSocket connections
py_connection_manager = BaseConnectionManager()

@app.websocket("/ws/py_client")
async def websocket_endpoint(websocket: WebSocket):
    # Accept and manage the WebSocket connection
    connection_id = await py_connection_manager.connect(websocket)
    
    # Send a simple "connect" event when the client connects
    await websocket.send_json({
        "event": "connect",
        "client_id": connection_id,
        "data": {}
    })

    try:
        # Handle incoming messages and events
        while True:
            message = await websocket.receive_json()
            event = WebsocketEvent(**message)
            print(f"Received event: {event.event}")
            # Handle the event logic here...

    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        await py_connection_manager.disconnect(connection_id)

```

## 3. Running the FastAPI Application
At the end of the script, the FastAPI application is run using the `uvicorn` ASGI server. This will make the WebSocket endpoint available to clients.

```python
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
```

Explanation:
uvicorn.run(...): This runs the FastAPI application, making the WebSocket endpoint available at ws://localhost:8000/ws/py_client.

4. Conclusion
In this phase, we've built a BaseConnectionManager class that allows FastAPI to handle WebSocket connections effectively. The manager:

Accepts new connections.
Tracks active connections.
Sends messages to specific clients.
Handles disconnections gracefully.
By managing WebSocket connections in this way, the server can handle real-time communication more efficiently, ensuring each client can be interacted with individually.


## 6. Full Code

To run the FastAPI app and start the WebSocket server, we use the `uvicorn` ASGI server.

```python
import uuid
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Literal
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Serve static files (optional, for assets like CSS, JS)
app.mount(
    "/static", StaticFiles(directory="static"), name="static"
)

# Set up templates for rendering HTML pages
templates = Jinja2Templates(directory="templates")

class WebsocketData(BaseModel):
    data: Dict[str, Any]

class WebsocketEvent(BaseModel):
    event: str
    client_id: str
    data: WebsocketData

class BaseConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        connection_id = str(uuid.uuid4())  # Generate a unique ID for each connection
        self.active_connections[connection_id] = websocket

    async def disconnect(self, connection_id: str) -> None:
        del self.active_connections[connection_id]

    async def send_to_client(self, client_id: str, message: dict) -> None:
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

py_connection_manager = BaseConnectionManager()

@app.websocket("/ws/py_client")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    connection_id = await py_connection_manager.connect(websocket)
    
    # Send a simple "connect" event when the client connects
    await websocket.send_json({
        "event": "connect",
        "client_id": connection_id,
        "data": {}
    })

    try:
        # Handle incoming messages
        while True:
            message = await websocket.receive_json()
            event = WebsocketEvent(**message)
            print(f"Received event: {event.event}")

    except Exception as e:
        print(f"Error: {e}")
        await py_connection_manager.disconnect(connection_id)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
```


**Explanation:**

- `uvicorn` is the ASGI server used to run the FastAPI application. 


