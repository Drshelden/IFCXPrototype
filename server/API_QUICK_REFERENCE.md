# API Quick Reference

## Core Endpoints

### Upload File
```bash
POST /api/upload
Content-Type: multipart/form-data

curl -F "file=@model.ifc" http://localhost:5000/api/upload
```

### Query Entity GUIDs
```bash
GET /api/entityGuids?models=MODEL&entity_types=TYPE

# Examples:
curl "http://localhost:5000/api/entityGuids"
curl "http://localhost:5000/api/entityGuids?models=HelloWall-2x3"
curl "http://localhost:5000/api/entityGuids?entity_types=IfcPropertySet"
curl "http://localhost:5000/api/entityGuids?models=HelloWall-2x3&entity_types=IfcWall"
```

### Query Component GUIDs
```bash
GET /api/componentGuids?models=MODEL&entity_guids=GUID&entity_types=TYPE

# Examples:
curl "http://localhost:5000/api/componentGuids"
curl "http://localhost:5000/api/componentGuids?models=HelloWall-2x3"
curl "http://localhost:5000/api/componentGuids?entity_types=IfcWallAttributes"
curl "http://localhost:5000/api/componentGuids?entity_guids=12345678-1234-5678-1234-567812345678"
```

### Get Component Data
```bash
GET /api/components?componentGuids=GUID1,GUID2,GUID3

# Example:
curl "http://localhost:5000/api/components?componentGuids=abc123,def456,ghi789"
```

## Helper Endpoints

### List All Models
```bash
GET /api/models
curl http://localhost:5000/api/models
```

### List Entity Types
```bash
GET /api/entity_types?models=MODEL1,MODEL2

# Examples:
curl http://localhost:5000/api/entity_types
curl "http://localhost:5000/api/entity_types?models=HelloWall-2x3"
```

### Server Status
```bash
GET /api/status
curl http://localhost:5000/api/status
```

### Refresh Memory Tree
```bash
POST /api/refresh
curl -X POST http://localhost:5000/api/refresh
```

## Complex Queries

### All walls in a model
```bash
curl "http://localhost:5000/api/entityGuids?models=HelloWall-2x3&entity_types=IfcWall"
```

### All property sets across models
```bash
curl "http://localhost:5000/api/entityGuids?entity_types=IfcPropertySet"
```

### Components for multiple entities
```bash
curl "http://localhost:5000/api/componentGuids?entity_guids=guid1,guid2,guid3"
```

### Specific types in multiple models
```bash
curl "http://localhost:5000/api/componentGuids?models=Model1,Model2&entity_types=IfcPropertySet"
```

## Python Examples

```python
import requests

BASE_URL = 'http://localhost:5000/api'

# Get all models
response = requests.get(f'{BASE_URL}/models')
models = response.json()  # Returns list of model names

# Get entity types
response = requests.get(f'{BASE_URL}/entity_types', 
                       params={'models': 'HelloWall-2x3'})
types = response.json()  # Returns list of type names

# Query entity GUIDs
response = requests.get(f'{BASE_URL}/entityGuids',
                       params={
                           'models': 'HelloWall-2x3',
                           'entity_types': 'IfcPropertySet'
                       })
entity_data = response.json()  # Returns {modelName: [guid1, guid2, ...]}

# Query component GUIDs
response = requests.get(f'{BASE_URL}/componentGuids',
                       params={
                           'models': 'HelloWall-2x3'
                       })
component_data = response.json()  # Returns {modelName: [guid1, guid2, ...]}

# Get component data
response = requests.get(f'{BASE_URL}/components',
                       params={'componentGuids': 'guid1,guid2,guid3'})
components = response.json()  # Returns [component1, component2, ...]

# Upload file
with open('myfile.ifc', 'rb') as f:
    response = requests.post(f'{BASE_URL}/upload',
                            files={'file': f})
result = response.json()
```

## Response Format

### List Endpoints
Returns a JSON array:
```json
["Model1", "Model2", "Model3"]
```

### Query Endpoints (entityGuids, componentGuids)
Returns a dictionary organized by model name:
```json
{
  "ModelName": ["guid1", "guid2", "guid3"]
}
```

### Components Endpoint
Returns a JSON array of component objects:
```json
[
  {
    "componentGuid": "...",
    "entityGuid": "...",
    "type": "IfcWall",
    "model": "ModelName",
    "properties": {...}
  }
]
```

### Error Response
```json
{
  "error": "Error message"
}
```

## Parameter Types

- **models**: Comma-separated model names
- **entity_types**: Comma-separated IFC type names
- **entity_guids**: Comma-separated entity GUIDs
- **componentGuids**: Comma-separated component GUIDs

## Common Filters

| Parameter | Values | Example |
|-----------|--------|---------|
| `models` | Model names | `HelloWall-2x3,AnotherModel` |
| `entity_types` | IFC types | `IfcWall,IfcDoor,IfcPropertySet` |
| `entity_guids` | UUID format | `12345678-1234-5678-1234-567812345678` |
| `componentGuids` | Component GUIDs | `abc123def456abc123def456abc123de` |

## Quick Start

1. **Check available models:**
   ```bash
   curl http://localhost:5000/api/models
   ```

2. **Get entity GUIDs for a model:**
   ```bash
   curl "http://localhost:5000/api/entityGuids?models=HelloWall-2x3"
   ```

3. **Get components for those entities:**
   ```bash
   curl "http://localhost:5000/api/componentGuids?models=HelloWall-2x3"
   ```

4. **Get full component data:**
   ```bash
   curl "http://localhost:5000/api/components?componentGuids=guid1,guid2"
   ```

## Status Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `413` - File too large
- `404` - Model or endpoint not found
- `500` - Server error
