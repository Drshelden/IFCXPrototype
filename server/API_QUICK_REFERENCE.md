# API Quick Reference

## Core Endpoints

### Upload File
```bash
POST /api/upload
Content-Type: multipart/form-data

curl -F "file=@model.ifc" http://localhost:5000/api/upload
```

### Query Entities
```bash
GET /api/entities?models=MODEL&entity_types=TYPE&components=GUID

# Examples:
curl "http://localhost:5000/api/entities"
curl "http://localhost:5000/api/entities?models=HelloWall"
curl "http://localhost:5000/api/entities?entity_types=IfcPropertySet"
curl "http://localhost:5000/api/entities?components=abc123,def456"
```

### Query Components
```bash
GET /api/guids?models=MODEL&entity_guids=GUID&entity_types=TYPE

# Examples:
curl "http://localhost:5000/api/guids"
curl "http://localhost:5000/api/guids?models=HelloWall"
curl "http://localhost:5000/api/guids?entity_types=IfcWallAttributes"
curl "http://localhost:5000/api/guids?entity_guids=12345678-1234-5678-1234-567812345678"
```

### Get Component Data
```bash
GET /api/components?guids=GUID1,GUID2,GUID3

# Example:
curl "http://localhost:5000/api/components?guids=abc123,def456,ghi789"
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
curl "http://localhost:5000/api/entity_types?models=HelloWall"
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
curl "http://localhost:5000/api/guids?models=HelloWall&entity_types=IfcWallAttributes"
```

### All property sets across models
```bash
curl "http://localhost:5000/api/guids?entity_types=IfcPropertySet"
```

### Components for multiple entities
```bash
curl "http://localhost:5000/api/guids?entity_guids=guid1,guid2,guid3"
```

### Specific types in multiple models
```bash
curl "http://localhost:5000/api/guids?models=Model1,Model2&entity_types=IfcPropertySet,IfcObjectDefinition"
```

## Python Examples

```python
import requests

BASE_URL = 'http://localhost:5000/api'

# Get all models
response = requests.get(f'{BASE_URL}/models')
models = response.json()['models']

# Get entity types
response = requests.get(f'{BASE_URL}/entity_types', 
                       params={'models': 'HelloWall'})
types = response.json()['entity_types']

# Query components
response = requests.get(f'{BASE_URL}/guids',
                       params={
                           'models': 'HelloWall',
                           'entity_types': 'IfcPropertySet'
                       })
component_guids = response.json()['component_guids']

# Get component data
response = requests.get(f'{BASE_URL}/components',
                       params={'guids': ','.join(component_guids[:10])})
components = response.json()['components']

# Upload file
with open('myfile.ifc', 'rb') as f:
    response = requests.post(f'{BASE_URL}/upload',
                            files={'file': f})
result = response.json()
```

## Response Format

All endpoints return JSON:

**Success:**
```json
{
  "success": true,
  "count": 10,
  "data": [...],
  ...
}
```

**Error:**
```json
{
  "error": "Error message"
}
```

## Parameter Types

- **models**: Comma-separated model names
- **entity_types**: Comma-separated type names
- **entity_guids**: Comma-separated entity GUIDs
- **components**: Comma-separated component GUIDs
- **guids**: Comma-separated component GUIDs

## Common Filters

| Parameter | Values | Example |
|-----------|--------|---------|
| `models` | Model names | `HelloWall,AnotherModel` |
| `entity_types` | IFC types sans "Component" | `IfcWallAttributes,IfcDoor` |
| `entity_guids` | UUID format | `12345678-1234-5678-1234-567812345678` |
| `components` | 32-char hex GUIDs | `abc123def456abc123def456abc123de` |
| `guids` | Same as components | `abc123,def456` |

## Status Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `413` - File too large
- `500` - Server error
