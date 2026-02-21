# IFC Processing Server - Examples

This directory contains practical examples of how to use the reorganized IFC Processing Server with its pluggable backend architecture.

## Quick Start

### Run All Examples
```bash
python example_usage.py
```

This will demonstrate:
1. Basic server usage
2. Factory function approach
3. Backend switching
4. Component querying
5. Environment configuration
6. API testing
7. Custom backend patterns

## Individual Examples

### Example 1: Basic Server Usage
```python
from server import IFCProcessingServer

# Create server with file-based backend
server = IFCProcessingServer(data_store_type='fileBased')

# Access components
print(f"Data Store: {server.data_store_type}")
print(f"Store Path: {server.file_store.base_path}")
print(f"Models: {server.memory_tree.get_models()}")
```

### Example 2: Using Factory Function
```python
from server import create_app

# Create Flask app
app = create_app(data_store_type='fileBased')

# Use with Flask development server
if __name__ == '__main__':
    app.run(debug=True)
```

### Example 3: Backend Switching
```python
from server import IFCProcessingServer

# File-based backend
server_file = IFCProcessingServer(data_store_type='fileBased')

# MongoDB backend (stub)
try:
    server_mongo = IFCProcessingServer(data_store_type='mongodbBased')
except NotImplementedError as e:
    print(f"MongoDB not implemented: {e}")
```

### Example 4: Querying Components
```python
from server import IFCProcessingServer

server = IFCProcessingServer(data_store_type='fileBased')
memory_tree = server.memory_tree

# Get all models
models = memory_tree.get_models()

# Query specific model
if models:
    model_name = models[0]
    
    # Get entity GUIDs
    entities = memory_tree.get_entity_guids(models=[model_name])
    
    # Get component GUIDs
    components = memory_tree.get_component_guids(models=[model_name])
    
    # Get components data
    comp_data, guid_to_model = memory_tree.get_components(components, models=[model_name])
    
    # Get entity types
    types = memory_tree.get_entity_types(models=[model_name])
```

### Example 5: Environment Configuration
```bash
# Set backend via environment variable
set IFC_DATA_STORE=fileBased
python server.py

# Or via programmatic environment setup
import os
os.environ['IFC_DATA_STORE'] = 'fileBased'
from server import IFCProcessingServer
server = IFCProcessingServer()
```

### Example 6: Testing API with Flask Test Client
```python
from server import IFCProcessingServer

server = IFCProcessingServer(data_store_type='fileBased')
client = server.app.test_client()

# Test endpoints
response = client.get('/api/status')
print(response.json)  # {"status": "running", "data_store": "fileBased", ...}

response = client.get('/api/stores')
print([s['name'] for s in response.json])  # ["fileBased", "mongodbBased"]

response = client.get('/api/models')
print(response.json)  # List of model names
```

### Example 7: Custom Backend Pattern

See `BACKEND_INTERFACE.md` for a complete PostgreSQL backend example.

## Real-World Use Cases

### Use Case 1: Multi-Model Queries
```python
from server import IFCProcessingServer

server = IFCProcessingServer(data_store_type='fileBased')
tree = server.memory_tree

# Query across all models
all_entities = tree.get_entity_guids()

# Query across specific models
models = ['Building_A', 'Building_B']
entities = tree.get_entity_guids(models=models)

# Query by entity type
walls = tree.get_entity_guids(entity_types=['IfcWall'])
```

### Use Case 2: Component-Based Queries
```python
# Find all components of specific type
beams = tree.get_component_guids(entity_types=['IfcBeam'])

# Get component data
beam_data, guid_to_model = tree.get_components(beams)

# Organize by model using the guid_to_model mapping
by_model = {}
for component in beam_data:
    guid = component.get('componentGuid')
    model_name = guid_to_model.get(guid, 'unknown')
    if model_name not in by_model:
        by_model[model_name] = []
    by_model[model_name].append(component)
```

### Use Case 3: Filtered Exploration
```python
# Find walls in specific model
model_walls = tree.get_entity_guids(
    models=['Building_A'],
    entity_types=['IfcWall']
)

# Get components for those walls
wall_components = tree.get_component_guids(
    models=['Building_A'],
    entity_guids=model_walls
)

# Retrieve full data
wall_data, guid_to_model = tree.get_components(
    wall_components,
    models=['Building_A']
)
```

### Use Case 4: Server Integration
```python
from server import create_app
from flask import jsonify

app = create_app('fileBased')

@app.route('/custom/walls')
def get_walls():
    """Custom endpoint for wall data"""
    # Access the server's memory tree via app.config or globals
    # Implementation depends on your setup
    pass

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## Testing

### Test File-Based Backend
```bash
# Start server
python -c "from server import IFCProcessingServer; s = IFCProcessingServer(); s.app.run()"

# In another terminal
curl http://localhost:5000/api/status
```

### Test Backend Interface
```python
# Test that both backends have same interface
from dataStores.fileBased import FileBasedStore as FileStore
from dataStores.fileBased import MemoryTree as FileMemoryTree

# Check methods exist
assert hasattr(FileStore, 'store')
assert hasattr(FileMemoryTree, 'get_entity_guids')
assert hasattr(FileMemoryTree, 'get_components')

print("✓ File-based backend has required interface")
```

### Test MongoDB Stub
```python
from dataStores.mongodbBased import MongoDBStore, MongoDBMemoryTree

# Verify stub methods raise NotImplementedError
try:
    store = MongoDBStore()
    store.store('test', [])
except NotImplementedError:
    print("✓ MongoDB correctly raises NotImplementedError (stub)")
```

## Common Patterns

### Pattern 1: Query Then Retrieve
```python
# 1. Use memory tree to find GUIDs (fast)
guids = server.memory_tree.get_component_guids(
    models=['Building_A'],
    entity_types=['IfcWall']
)

# 2. Retrieve full components (gets additional data)
components, guid_to_model = server.memory_tree.get_components(guids)

# 3. Process data
for component in components:
    print(component['componentType'])
```

### Pattern 2: Model Exploration
```python
# List all models
models = server.memory_tree.get_models()

for model_name in models:
    # Explore model
    entities = server.memory_tree.get_entity_guids(models=[model_name])
    types = server.memory_tree.get_entity_types(models=[model_name])
    
    print(f"Model: {model_name}")
    print(f"  Entities: {len(entities)}")
    print(f"  Types: {types}")
```

### Pattern 3: Type-Based Filtering
```python
# Get all entity types
all_types = server.memory_tree.get_entity_types()

# For each type, get entities and components
for entity_type in all_types:
    entities = server.memory_tree.get_entity_guids(entity_types=[entity_type])
    components = server.memory_tree.get_component_guids(entity_types=[entity_type])
    
    print(f"{entity_type}: {len(entities)} entities, {len(components)} components")
```

## Documentation References

- **[REORGANIZATION.md](../REORGANIZATION.md)** - Complete architecture overview
- **[QUICK_START.md](../QUICK_START.md)** - How to start the server
- **[BACKEND_INTERFACE.md](../BACKEND_INTERFACE.md)** - How to implement backends
- **[PROJECT_REORGANIZATION.md](../PROJECT_REORGANIZATION.md)** - Summary of changes
- **[VERIFICATION_CHECKLIST.md](../VERIFICATION_CHECKLIST.md)** - Verification steps

## Running Examples

### Prerequisites
```bash
# Ensure in project root
cd c:\_LOCAL\GitHub\IFCXPrototype\server

# Activate virtual environment if needed
.venv\Scripts\Activate.ps1
```

### Run All Examples
```bash
python examples/example_usage.py
```

### Run Individual Examples
```python
# In Python REPL
from examples.example_usage import example_basic_usage
example_basic_usage()
```

### Run Your Own Example
```python
# Create your_example.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import IFCProcessingServer

server = IFCProcessingServer(data_store_type='fileBased')
print(f"Models: {server.memory_tree.get_models()}")
```

## Troubleshooting Examples

| Issue | Solution |
|-------|----------|
| Import error | Ensure PYTHONPATH includes server root |
| FileNotFoundError | Check working directory is server root |
| MongoDB NotImplementedError | This is expected (stub), implement MongoDB when needed |
| Port already in use | Kill existing server or use different port |

## Next Steps

1. **Run the examples**: `python examples/example_usage.py`
2. **Start the server**: `python server.py` or `python ifcxServerFileStore.py`
3. **Upload test data**: Use admin interface at http://localhost:5000
4. **Test queries**: Use API endpoints
5. **Implement MongoDB**: Follow BACKEND_INTERFACE.md guide

---

**Questions or Issues?**
- Check [QUICK_START.md](../QUICK_START.md) for common startup issues
- Review [BACKEND_INTERFACE.md](../BACKEND_INTERFACE.md) for backend development
- See [REORGANIZATION.md](../REORGANIZATION.md) for architecture questions
