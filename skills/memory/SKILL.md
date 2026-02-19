---
name: Memory MCP
description: Tools for interacting with the knowledge graph (memory).
---

# Memory MCP

The Memory MCP server provides tools to manipulate a knowledge graph. This graph consists of **entities** (nodes), **relations** (edges), and **observations** (attributes/notes attached to entities).

## Core Concepts

- **Entity**: A node in the graph. Defined by a `name` and an `entityType`.
- **Relation**: A directed edge between two entities. Defined by `from`, `to`, and `relationType`.
- **Observation**: A piece of textual information attached to an entity.

## Tools

### 1. `create_entities`
Create multiple new entities in the knowledge graph.

**Parameters:**
- `entities`: List of objects, each containing:
    - `name`: Name of the entity (string).
    - `entityType`: Type of the entity (string, e.g., "Person", "Project").
    - `observations`: List of initial observations (list of strings).

**Example:**
```json
{
  "entities": [
    {
      "name": "Project Alpha",
      "entityType": "Project",
      "observations": ["High priority", "Due next month"]
    }
  ]
}
```

### 2. `create_relations`
Create multiple new relations between entities. Relations should be in active voice.

**Parameters:**
- `relations`: List of objects, each containing:
    - `from`: Name of the source entity.
    - `to`: Name of the target entity.
    - `relationType`: Type of the relation (e.g., "contains", "managed_by").

**Example:**
```json
{
  "relations": [
    {
      "from": "Project Alpha",
      "to": "Alice",
      "relationType": "managed_by"
    }
  ]
}
```

### 3. `add_observations`
Add new observations to existing entities.

**Parameters:**
- `observations`: List of objects, each containing:
    - `entityName`: Name of the entity.
    - `contents`: List of observation strings.

### 4. `delete_entities`
Delete multiple entities and their associated relations.

**Parameters:**
- `entityNames`: List of entity names to delete.

### 5. `delete_observations`
Delete specific observations from entities.

**Parameters:**
- `deletions`: List of objects specifying `entityName` and `observations` to delete.

### 6. `delete_relations`
Delete multiple relations.

**Parameters:**
- `relations`: List of relation objects (`from`, `to`, `relationType`) to delete.

### 7. `read_graph`
Read the entire knowledge graph. Returns all entities and relations.

### 8. `search_nodes`
Search for nodes in the knowledge graph based on a query.

**Parameters:**
- `query`: The search query string.

### 9. `open_nodes`
Open specific nodes by their names.

**Parameters:**
- `names`: List of entity names to retrieve.

## Usage Workflow

1.  **Search**: Use `search_nodes` to check if relevant entities exist.
2.  **Create/Update**: Use `create_entities` to add new nodes or `add_observations` to add details. Use `create_relations` to link them.
3.  **Explore**: Use `open_nodes` or `read_graph` to inspect the graph structure.
