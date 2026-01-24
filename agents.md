# Lightroom MCP Agents

This document describes how AI agents can interact with Adobe Lightroom Classic through the Model Context Protocol (MCP) server.

## Overview

The Lightroom MCP server provides a bridge between AI agents and Adobe Lightroom Classic, enabling automated photo management, metadata editing, and catalog operations. Agents can query photo information, modify ratings, labels, and captions, and retrieve catalog details.

## Architecture

The system consists of two main components:

1. **Lightroom Plugin** (`lightroom-plugin.lrplugin/`): A Lua plugin that runs inside Lightroom Classic and handles commands via a local socket connection (port 54321).

2. **MCP Server** (`mcp-server/`): A Python FastMCP server that exposes Lightroom functionality as MCP tools, allowing AI agents to interact with Lightroom through standardized tool calls.

## Available Tools

### `get_studio_info() -> str`

Retrieves information about the active Lightroom catalog.

**Returns:** JSON string containing:
- `catalogName`: Name of the active catalog
- `catalogPath`: File system path to the catalog
- `pluginVersion`: Version of the MCP Bridge plugin

**Use Cases:**
- Verify Lightroom connection
- Identify which catalog is active
- Check plugin availability

**Example Agent Usage:**
```
"Get information about the current Lightroom catalog"
→ Calls get_studio_info()
→ Returns: {"catalogName": "My Photos", "catalogPath": "/Users/...", "pluginVersion": "0.1.0"}
```

### `get_selection() -> str`

Gets details about currently selected photos in Lightroom.

**Returns:** JSON string containing an array of photo objects with:
- `localId`: Unique identifier for the photo
- `filename`: Formatted filename
- `path`: Full file system path
- `rating`: Star rating (0-5)
- `label`: Color label (red, yellow, green, blue, purple, or null)
- `title`: Photo title
- `caption`: Photo caption

**Use Cases:**
- Analyze selected photos
- Review metadata before making changes
- Batch operations on selected photos
- Photo organization workflows

**Example Agent Usage:**
```
"Show me details about the selected photos"
→ Calls get_selection()
→ Returns: {"photos": [{"filename": "IMG_001.jpg", "rating": 3, ...}, ...]}
```

### `set_rating(rating: int) -> str`

Sets the star rating for currently selected photos.

**Parameters:**
- `rating`: Integer between 0 and 5

**Returns:** "Success" or error message

**Use Cases:**
- Automated photo culling
- Quality-based organization
- Workflow automation (e.g., "Rate all selected photos as 4 stars")

**Example Agent Usage:**
```
"Rate the selected photos 5 stars"
→ Calls set_rating(5)
→ Returns: "Success"
```

### `set_label(label: str) -> str`

Sets the color label for currently selected photos.

**Parameters:**
- `label`: One of 'Red', 'Yellow', 'Green', 'Blue', 'Purple', 'None'

**Returns:** "Success" or error message

**Use Cases:**
- Categorize photos by color labels
- Mark photos for specific workflows
- Visual organization and filtering

**Example Agent Usage:**
```
"Mark these photos with a green label"
→ Calls set_label("Green")
→ Returns: "Success"
```

### `set_caption(caption: str) -> str`

Sets the caption for currently selected photos.

**Parameters:**
- `caption`: Text caption to apply

**Returns:** "Success" or error message

**Use Cases:**
- Automated caption generation
- Batch caption updates
- Adding descriptions to photos

**Example Agent Usage:**
```
"Add the caption 'Sunset at the beach' to selected photos"
→ Calls set_caption("Sunset at the beach")
→ Returns: "Success"
```

## Agent Workflows

### Workflow 1: Photo Culling Assistant

An agent can help photographers cull through large batches of photos:

1. User selects photos in Lightroom
2. Agent calls `get_selection()` to retrieve photo details
3. Agent analyzes filenames, existing ratings, or other metadata
4. Agent calls `set_rating()` to mark keepers/rejects
5. Agent calls `set_label()` to categorize photos

**Example:**
```
User: "Rate all selected photos 3 stars, then mark the best ones 5 stars"
Agent:
  1. get_selection() → Analyze photos
  2. set_rating(3) → Rate all as 3
  3. [Agent logic to identify "best" photos]
  4. set_rating(5) → Rate best ones as 5
```

### Workflow 2: Metadata Enhancement

An agent can enhance photo metadata:

1. Agent calls `get_selection()` to get current metadata
2. Agent generates or updates captions based on filenames, dates, or other context
3. Agent calls `set_caption()` to apply new captions
4. Agent calls `set_label()` to organize by content

**Example:**
```
User: "Add descriptive captions to these photos based on their filenames"
Agent:
  1. get_selection() → Get filenames
  2. [Generate captions from filenames]
  3. set_caption("Generated caption") → Apply to each photo
```

### Workflow 3: Catalog Management

An agent can help manage and organize catalogs:

1. Agent calls `get_studio_info()` to verify connection
2. Agent calls `get_selection()` to understand current state
3. Agent performs batch operations based on user requests

**Example:**
```
User: "What catalog am I working with?"
Agent:
  1. get_studio_info() → Returns catalog details
  2. Reports: "You're working with catalog 'My Photos' at /path/to/catalog"
```

## Best Practices for Agents

1. **Always verify connection first**: Call `get_studio_info()` to ensure Lightroom is running and the plugin is active.

2. **Check selection before modifying**: Call `get_selection()` to see what photos will be affected before making changes.

3. **Handle errors gracefully**: All tools return error messages that agents should parse and report to users.

4. **Batch operations**: The tools operate on all selected photos, so agents should inform users about the scope of operations.

5. **Respect user intent**: Agents should confirm destructive operations or operations affecting many photos.

6. **Provide feedback**: After operations, agents can call `get_selection()` again to verify changes were applied.

## Error Handling

All tools may return error messages in the following format:
- `"Error: {error message}"` - Specific error from Lightroom or the plugin
- `"Error: No response from Lightroom"` - Connection or communication issue
- `"Error: Rating must be between 0 and 5"` - Validation error

Agents should:
- Parse error messages and provide user-friendly feedback
- Retry operations if connection errors occur
- Validate parameters before calling tools (e.g., rating range, label values)

## Technical Notes

- **Connection**: The MCP server connects to Lightroom via localhost:54321
- **Protocol**: JSON-RPC 2.0 over TCP socket
- **Threading**: Operations are synchronous; agents should wait for responses
- **Selection-based**: All metadata operations work on currently selected photos in Lightroom
- **Write Access**: Metadata changes require write access to the catalog (handled automatically by the plugin)

## Future Enhancements

Potential additions for agent workflows:
- Photo search and filtering
- Collection management
- Keyword operations
- Develop settings access
- Export operations
- Smart collection creation
