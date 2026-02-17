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
GET /api/components?[componentGuids=GUID1,GUID2] | [models=MODEL] | [entity_types=TYPE] | [entity_guids=GUID]

# Examples:
curl "http://localhost:5000/api/components"  # All components
curl "http://localhost:5000/api/components?componentGuids=abc123,def456"  # Specific components
curl "http://localhost:5000/api/components?models=HelloWall-01"  # All components in model
curl "http://localhost:5000/api/components?entity_types=IfcWallStandardCase"  # By entity type
curl "http://localhost:5000/api/components?models=HelloWall-01&entity_types=IfcWallStandardCase"  # Combined filters
curl "http://localhost:5000/api/components?entity_guids=guid1,guid2"  # For specific entities
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
curl "http://localhost:5000/api/entityGuids?models=HelloWall-01&entity_types=IfcWallStandardCase"
```

### All wall components with full data
```bash
curl "http://localhost:5000/api/components?models=HelloWall-01&entity_types=IfcWallStandardCase"
```

### All property sets across models
```bash
curl "http://localhost:5000/api/entityGuids?entity_types=IfcPropertySet"
```

### Components for multiple entities
```bash
curl "http://localhost:5000/api/componentGuids?entity_guids=guid1,guid2,guid3"
```

### Full component data for multiple entities
```bash
curl "http://localhost:5000/api/components?entity_guids=guid1,guid2,guid3"
```

### Specific types in multiple models
```bash
curl "http://localhost:5000/api/componentGuids?models=Model1,Model2&entity_types=IfcPropertySet"
```

### Full component data for specific types across models
```bash
curl "http://localhost:5000/api/components?models=Model1,Model2&entity_types=IfcPropertySet"
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

# Get component data by specific GUIDs
response = requests.get(f'{BASE_URL}/components',
                       params={'componentGuids': 'guid1,guid2,guid3'})
components_by_model = response.json()  # Returns {modelName: [component1, component2, ...]}

# Get all components in a model
response = requests.get(f'{BASE_URL}/components',
                       params={'models': 'HelloWall-01'})
components_by_model = response.json()

# Get components by entity type
response = requests.get(f'{BASE_URL}/components',
                       params={'entity_types': 'IfcWallStandardCase'})
components_by_model = response.json()

# Get components for specific entities
response = requests.get(f'{BASE_URL}/components',
                       params={'entity_guids': 'guid1,guid2'})
components_by_model = response.json()

# Combined filters
response = requests.get(f'{BASE_URL}/components',
                       params={
                           'models': 'HelloWall-01',
                           'entity_types': 'IfcWallStandardCase'
                       })
components_by_model = response.json()

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
Returns a dictionary organized by model name, with each model containing an array of component objects:
```json
{
  "HelloWall-01": [
    {
      "componentGuid": "5d7be3a6-fe8b-0924-729b-33cd0f175b6a",
      "componentName": "Basic Wall:Generic - 8\"",
      "componentType": "IfcWallStandardCaseComponent",
      "entityGuid": "0d68ad35-29c7-484d-907c-65a3fbc0eadb",
      "entityType": "IfcWallStandardCase",
      "objectType": "Basic Wall:Generic - 8\"",
      "tag": "1240542",
      "model": "HelloWall-01"
    },
    {
      "componentGuid": "abc123...",
      ...
    }
  ],
  "HelloWall-02": [
    {...}
  ]
}
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
   curl "http://localhost:5000/api/entityGuids?models=HelloWall-01"
   ```

3. **Get components for those entities:**
   ```bash
   curl "http://localhost:5000/api/componentGuids?models=HelloWall-01"
   ```

4. **Get full component data (with filtering):**
   ```bash
   curl "http://localhost:5000/api/components?models=HelloWall-01"
   curl "http://localhost:5000/api/components?entity_types=IfcWallStandardCase"
   curl "http://localhost:5000/api/components?componentGuids=guid1,guid2"
   ```

## Status Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `413` - File too large
- `404` - Model or endpoint not found
- `500` - Server error
