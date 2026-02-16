# IFC Processing Server - API Documentation

## Overview

The IFC Processing Server provides a comprehensive REST API for uploading, processing, and querying IFC (Industry Foundation Classes) data. The server maintains an in-memory tree structure for fast component querying across multiple models.

## Memory Tree Architecture

The server loads all components from disk into an organized in-memory tree structure when it starts or when new files are uploaded:

```
models/
├── HelloWallIFCjsonC-2x3/
│   ├── by_entity: { entityGuid -> [componentGuids] }
│   ├── by_type: { componentType -> [componentGuids] }
│   └── by_guid: { componentGuid -> componentData }
├── AnotherModel/
│   ├── by_entity: { ... }
│   ├── by_type: { ... }
│   └── by_guid: { ... }
```

### Tree Structure Details

- **by_entity**: Maps entity GUIDs to lists of all component GUIDs belonging to that entity
- **by_type**: Maps component types (with "Component" suffix removed) to lists of component GUIDs of that type
  - Example: `IfcDoorStyleComponent` → stored as `IfcDoorStyle`
- **by_guid**: Maps component GUIDs to full component data for direct retrieval

## API Endpoints

### Upload & Process

#### POST `/api/upload`

Upload and process IFC or JSON files.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): IFC or JSON file to upload (Max 500MB)

**Response:**
```json
{
  "success": true,
  "filename": "HelloWall.json",
  "entities_count": 13,
  "stored_count": 13,
  "store_path": "/path/to/dataStores/fileBased/data/HelloWall",
  "message": "Successfully processed 13 entities"
}
```

**Notes:**
- IFC files are automatically converted to JSON components
- JSON files must contain an array of components at root level
- Uploads refresh the in-memory tree automatically

---

### Query Endpoints

#### GET `/api/entities`

Query for entity GUIDs based on filters.

**Parameters:**
- `models` (optional): Comma-separated list of model names
  - Example: `models=HelloWall,AnotherModel`
  - Default: All models
- `entity_types` (optional): Comma-separated list of entity types to filter by
  - Example: `entity_types=IfcWallAttributes,IfcObjectDefinition`
  - Default: All types
- `components` (optional): Comma-separated list of component GUIDs to filter by
  - Default: All components

**Response:**
```json
{
  "success": true,
  "count": 2,
  "entity_guids": [
    "12345678-1234-5678-1234-567812345678",
    "87654321-4321-8765-4321-876543218765"
  ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/entities?models=HelloWall&entity_types=IfcWallAttributes"
```

---

#### GET `/api/guids`

Query for component GUIDs based on filters.

**Parameters:**
- `models` (optional): Comma-separated list of model names
  - Default: All models
- `entity_guids` (optional): Comma-separated list of entity GUIDs to filter by
  - Example: `entity_guids=12345678-1234-5678-1234-567812345678`
  - Default: All entities
- `entity_types` (optional): Comma-separated list of entity types
  - Default: All types

**Response:**
```json
{
  "success": true,
  "count": 3,
  "component_guids": [
    "abc123def456abc123def456abc123de",
    "def456abc123def456abc123def456ab",
    "456abc123def456abc123def456abc12"
  ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/guids?models=HelloWall&entity_types=IfcWallAttributes"
```

---

#### GET `/api/components`

Retrieve actual component data by GUIDs.

**Parameters:**
- `guids` (required): Comma-separated list of component GUIDs
  - Example: `guids=abc123def456,def456abc123`

**Response:**
```json
{
  "success": true,
  "count": 2,
  "components": [
    {
      "guid": "abc123def456abc123def456abc123de",
      "componentType": "IfcWallAttributesComponent",
      "entityGuid": "12345678-1234-5678-1234-567812345678",
      "name": "Wall-001",
      "description": "Exterior wall"
    },
    {
      "guid": "def456abc123def456abc123def456ab",
      "componentType": "IfcWallAttributesComponent",
      "entityGuid": "87654321-4321-8765-4321-876543218765",
      "name": "Wall-002",
      "description": "Interior wall"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/components?guids=abc123def456,def456abc123"
```

---

### Information Endpoints

#### GET `/api/models`

List all loaded models in the server.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "models": [
    "HelloWall",
    "AnotherModel"
  ]
}
```

---

#### GET `/api/entity_types`

List all entity types across models.

**Parameters:**
- `models` (optional): Comma-separated list of model names to filter by

**Response:**
```json
{
  "success": true,
  "count": 5,
  "entity_types": [
    "IfcDoorStyle",
    "IfcObjectDefinition",
    "IfcPropertySet",
    "IfcWallAttributes",
    "IfcWindowStyle"
  ]
}
```

---

#### GET `/api/status`

Get server status and version.

**Response:**
```json
{
  "status": "running",
  "timestamp": "2026-02-15T10:30:45.123456",
  "version": "0.0.1"
}
```

---

### Administration

#### POST `/api/refresh`

Manually refresh the in-memory component tree from disk.

**Response:**
```json
{
  "success": true,
  "models_loaded": 2,
  "message": "Memory tree refreshed with 2 model(s)"
}
```

**Use Cases:**
- After manually modifying files in the data store directory
- To force a full reload of components
- For troubleshooting data consistency issues

---

## Query Examples

### Get all property sets
```bash
curl "http://localhost:5000/api/guids?entity_types=IfcPropertySet"
```

### Get components for specific entity
```bash
curl "http://localhost:5000/api/guids?entity_guids=12345678-1234-5678-1234-567812345678"
```

### Get all entities in a model
```bash
curl "http://localhost:5000/api/entities?models=HelloWall"
```

### Retrieve component data
```bash
curl "http://localhost:5000/api/components?guids=abc123,def456,ghi789"
```

### Complex query: Walls in specific model
```bash
curl "http://localhost:5000/api/guids?models=HelloWall&entity_types=IfcWallAttributes"
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK**: Successful request
- **400 Bad Request**: Invalid parameters or missing required fields
- **413 Request Entity Too Large**: File upload exceeds size limit
- **500 Internal Server Error**: Server error during processing

**Error Response Format:**
```json
{
  "error": "Invalid parameters or descriptive error message"
}
```

---

## Performance Considerations

- **Memory Tree**: Loaded entirely into RAM for fast queries
- **Component Storage**: Stored as individual JSON files on disk
- **Query Speed**: O(1) for by_guid lookups, O(n) for by_type/by_entity iterations
- **Large Models**: Consider model size limitations based on available RAM

---

## Component Structure

Each component contains:
- `guid`: Internal component identifier
- `componentType`: Type with "Component" suffix (e.g., `IfcWallAttributesComponent`)
- `entityGuid`: Reference to the entity this component describes (optional)
- Additional properties specific to the component type

---

## Best Practices

1. **Use specific filters** when querying to reduce result size
2. **Batch requests** when retrieving multiple components
3. **Cache results locally** for frequently accessed data
4. **Monitor server memory** for models with millions of components
5. **Use models filter** to partition queries across multiple loaded models
