# Lightroom MCP Server

This directory contains the Python components of the Lightroom MCP bridge.

## Components

### 1. MCP Server (`server.py`)
This is the entry point that Cursor attempts to run. It uses `FastMCP` to expose tools to the AI agent.
- connect to `broker.py` to relay commands to Lightroom.
- Uses `lrc_client.py` as a client library.
- **Auto-starts the Broker** if it is not running.

### 2. Broker (`broker.py`)
A lightweight [Flask](https://flask.palletsprojects.com/) server that acts as a middleman between the ephemeral MCP process and the long-running Lightroom instance.
- **Port 8085 (HTTP)**: API for `lrc_client` and Web Dashboard.
- **Port 8086 (Socket)**: Persistent connection for the Lightroom Lua plugin.
- **Dashboard**: Open [http://localhost:8085](http://localhost:8085) to view logs, request history, and connection status.

### 3. Client Library (`lrc_client.py`)
Helper library used by `server.py` to communicate with the Broker.

## Setup & Development

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Running Manually

You can run the broker standalone for testing:

```bash
python start_broker.py
```

Or run the MCP server (though usually Cursor runs this):

```bash
python server.py
```

## Troubleshooting

- **Missing dependencies**: Ensure `pip install -r requirements.txt` succeeded.
- **Port in use**: Check if something else is using port 8085 or 8086.
- **Pillow / RawPy**: Image preview features require these libraries (included in requirements.txt).
