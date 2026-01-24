# Lightroom MCP

Bridge between [Adobe Lightroom Classic](https://www.adobe.com/products/photoshop-lightroom-classic.html) and AI agents via the [Model Context Protocol](https://modelcontextprotocol.io/) (MCP). Enables automated photo management, metadata editing, and catalog operations from Cursor and other MCP-capable clients.

## Architecture

- **Lightroom Plugin** (`lightroom-plugin.lrplugin/`) — Lua plugin running inside Lightroom Classic. Listens on `localhost:54321` and handles commands over a TCP socket (JSON-RPC 2.0).
- **MCP Server** (`mcp-server/`) — Python [FastMCP](https://github.com/jlowin/fastmcp) server that exposes Lightroom as MCP tools and connects to the plugin.

```
┌─────────────────┐     MCP      ┌──────────────┐  TCP :54321  ┌─────────────────────┐
│ Cursor / Agent  │ ◄──────────► │ MCP Server   │ ◄──────────► │ Lightroom + Plugin  │
└─────────────────┘              └──────────────┘              └─────────────────────┘
```

## Prerequisites

- **Adobe Lightroom Classic** (LrSdk 10.0+)
- **Python 3.10+** (for the MCP server)
- **Lightroom** and **MCP server** both running, with the plugin loaded

## Setup

### 1. Install the Lightroom plugin

1. Copy `lightroom-plugin.lrplugin` into your Lightroom plugins folder:
   - **macOS:** `~/Library/Application Support/Adobe/Lightroom/Modules/`
   - **Windows:** `%APPDATA%\Adobe\Lightroom\Modules\`
2. In Lightroom: **File → Plug-in Manager → Add** and select the plugin folder, or place it in **Modules** and restart Lightroom.
3. Ensure the plugin is **Enabled**. It starts a TCP server on port **54321** when Lightroom launches.

### 2. MCP server (Python)

```bash
cd mcp-server
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 3. Configure Cursor to use the MCP server

Add the Lightroom MCP server to your Cursor MCP config (e.g. **Settings → MCP** or `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json`):

```json
{
  "mcpServers": {
    "lightroom": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "d:/Projects/lightroom-mcp/mcp-server",
      "env": {}
    }
  }
}
```

Use the path to your project’s `mcp-server` folder for `cwd`. Run from a venv where `pip install -r requirements.txt` was executed so `lrc_client` and FastMCP are available.

## Usage

With the plugin loaded in Lightroom and the MCP server configured in Cursor:

1. Open a catalog in Lightroom Classic.
2. Select one or more photos.
3. In Cursor, use natural language or MCP tools to:
   - **Get catalog info** — `get_studio_info`
   - **Inspect selection** — `get_selection` (filenames, paths, rating, label, title, caption)
   - **Set rating** — `set_rating(0–5)`
   - **Set color label** — `set_label("Red"|"Yellow"|"Green"|"Blue"|"Purple"|"None")`
   - **Set caption** — `set_caption("your text")`

See **[agents.md](./agents.md)** for detailed tool semantics, example workflows, and best practices for AI agents.

## Project layout

```
lightroom-mcp/
├── README.md           # This file
├── agents.md           # MCP tools & agent workflows
├── CHANGELOG.md        # Version history
├── CONTRIBUTING.md     # Contribution guidelines
├── .cursorrules        # Cursor project rules
├── lightroom-plugin.lrplugin/   # Lua plugin for Lightroom
│   ├── Info.lua
│   ├── Init.lua
│   ├── Shutdown.lua
│   ├── Server.lua
│   ├── CommandHandlers.lua
│   └── JSON.lua
└── mcp-server/         # Python MCP server
    ├── server.py
    ├── lrc_client.py
    ├── test_connection.py
    └── requirements.txt
```

## Troubleshooting

- **"No response from Lightroom"** — Lightroom must be running, plugin enabled, and nothing else using port **54321**. Restart Lightroom and try again.
- **MCP server fails to start** — Check Python version, venv, and `pip install -r requirements.txt`. Run from `mcp-server` or set `cwd` correctly in MCP config.
- **Tools fail** — Ensure photos are selected when using `set_rating`, `set_label`, or `set_caption`. Call `get_selection` first to verify.

## License

See repository license file.
