# IFC Processing Server - Project Reorganization

## Overview

The project has been reorganized to support multiple data store backends with a pluggable architecture. This allows for easy switching between file-based and MongoDB-based storage while maintaining the same API interface.

## New Architecture

### Directory Structure

```
server/
├── server.py                          # Core Flask server with backend selection
├── ifcxServerFileStore.py             # Startup script (now references server.py)
├── app.py                             # Legacy file - can be removed
├── memoryTree.py                      # Legacy file - moved to dataStores/fileBased/
│
├── dataStores/
│   ├── __init__.py
│   ├── fileBased/                     # File-based storage backend
│   │   ├── __init__.py               # Exports FileBasedStore, MemoryTree
│   │   ├── fileBased.py              # FileBasedStore class
│   │   ├── memoryTree.py             # MemoryTree class for file-based
│   │   ├── data/                     # Actual stored component JSON files
│   │   │   ├── [ModelName]/
│   │   │   │   ├── [entityGuid]_[componentGuid].json
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── [Other future file-based utilities]
│   │
│   └── mongodbBased/                 # MongoDB storage backend (stub)
│       ├── __init__.py               # Exports MongoDBStore, MongoDBMemoryTree
│       ├── mongodbBased.py           # MongoDBStore class (interface + stub)
│       ├── mongodbMemoryTree.py      # MongoDBMemoryTree class (interface + stub)
│       └── [Other future MongoDB utilities]
│
├── ingestors/                         # IFC file processors
│   ├── ifc4ingestor.py               # IFC to JSON conversion
│   ├── utils.py
│   └── [Other ingestors]
│
├── templates/                         # HTML templates
│   ├── admin.html
│   ├── viewer.html
│   └── [Other templates]
│
├── utils/                             # IFC schema utilities (separate from dataStores)
│   ├── generate_ifc_hierarchy.py
│   ├── generate_ifc_flat.py
│   ├── ifc_hierarchy_query.py
│   ├── [Other IFC utilities]
│   └── [Generated output files]
│
├── docs/                              # Documentation
├── tests/                             # Tests
├── uploads/                           # Temporary upload folder
└── requirements.txt
```

## Backend Selection

### File-Based (Default)

**Usage:**
```bash
python ifcxServerFileStore.py
# Then choose option 1, or automatically uses fileBased

# Or directly:
python server.py

# Or set environment variable:
set IFC_DATA_STORE=fileBased
python server.py
```

**Characteristics:**
- Components stored as individual JSON files
- Simple, no external dependencies beyond Flask
- Directory structure: `dataStores/fileBased/data/[ModelName]/[entityGuid]_[componentGuid].json`
- MemoryTree loads files into memory for fast queries
- Best for: Development, testing, small datasets

**Files:**
- `dataStores/fileBased/fileBased.py` - FileBasedStore class
- `dataStores/fileBased/memoryTree.py` - MemoryTree class

### MongoDB-Based (Future)

**Usage:**
```bash
python ifcxServerFileStore.py
# Then choose option 2

# Or directly:
set IFC_DATA_STORE=mongodbBased
python server.py
```

**Characteristics:**
- Components stored in MongoDB collections
- Requires MongoDB server running
- Supports indexing, aggregation, advanced querying
- Scales to large datasets
- Best for: Production, large datasets, distributed systems

**Status:** Currently stub implementation
**To Implement:**
1. Install MongoDB (`brew install mongodb-community` or container)
2. Configure connection string in MongoDBStoreConfig
3. Implement database operations in MongoDBStore
4. Implement memory tree operations in MongoDBMemoryTree

## API - Core Server Entry Point

### `server.py`

The main Flask application with backend-agnostic architecture.

**Key Components:**

1. **IFCProcessingServer Class**
   - Encapsulates Flask app configuration
   - Manages backend initialization
   - Routes requests to appropriate backend

2. **Factory Function**
   ```python
   app = create_app(data_store_type='fileBased')
   ```

3. **Usage:**
   ```python
   from server import IFCProcessingServer
   
   server = IFCProcessingServer(data_store_type='fileBased')
   server.app.run()
   ```

## Backend Interface Contract

### Store Interface

Both backends must implement:

```python
class DataStore:
    def store(self, filename: str, components: List[Dict]) -> Dict:
        """Store components from a file"""
        pass
    
    def retrieve(self, directory: str) -> List[Dict]:
        """Retrieve all components from a directory/model"""
        pass
    
    def list_directories(self) -> List[Dict]:
        """List all stored directories/models"""
        pass
```

### Memory Tree Interface

Both backends must implement:

```python
class QueryableMemoryTree:
    def refresh(self) -> int:
        """Refresh tree from backend"""
        pass
    
    def get_entity_guids(self, models=None, entity_types=None, components=None) -> List[str]:
        """Query for entity GUIDs"""
        pass
    
    def get_component_guids(self, models=None, entity_guids=None, entity_types=None) -> List[str]:
        """Query for component GUIDs"""
        pass
    
    def get_components(self, guids: List[str], models=None) -> List[Dict]:
        """Retrieve component data"""
        pass
    
    def get_models(self) -> List[str]:
        """List all models"""
        pass
    
    def get_entity_types(self, models=None) -> List[str]:
        """List entity types"""
        pass
```

## Migration Path

### From Old Structure to New

**Old:**
- `app.py` - Flask routes (root level)
- `memoryTree.py` - Query engine (root level)
- `dataStores/fileBased/fileBased.py` - File store

**New:**
- `server.py` - Flask routes (root level, backend-agnostic)
- `dataStores/fileBased/memoryTree.py` - Query engine (backend-specific)
- `dataStores/fileBased/fileBased.py` - File store (unchanged)

### Upgrading Existing Code

If you have code referencing the old structure:

**Old imports:**
```python
from app import app
from dataStores.fileBased import FileBasedStore
from memoryTree import MemoryTree
```

**New imports:**
```python
from server import create_app, IFCProcessingServer
from dataStores.fileBased import FileBasedStore, MemoryTree
```

**Old app creation:**
```python
app = Flask(__name__)
file_store = FileBasedStore()
memory_tree = MemoryTree()
```

**New app creation:**
```python
# Option 1: Factory function
app = create_app(data_store_type='fileBased')

# Option 2: Full control
server = IFCProcessingServer(data_store_type='fileBased')
app = server.app
file_store = server.file_store
memory_tree = server.memory_tree
```

## Configuration

### Environment Variables

```bash
# Select data store backend
set IFC_DATA_STORE=fileBased        # or mongodbBased

# For MongoDB backend (future)
set MONGODB_URI=mongodb://localhost:27017
set MONGODB_DB=ifc_processing

# Server settings
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000
set FLASK_DEBUG=False
```

### Programmatic Configuration

```python
from server import IFCProcessingServer

# Use default file-based store
server = IFCProcessingServer()

# Use MongoDB store
server = IFCProcessingServer(data_store_type='mongodbBased')

# Get current store
print(server.data_store_type)  # 'fileBased' or 'mongodbBased'
print(server.app.config['DATA_STORE_TYPE'])
```

## API Endpoints

All endpoints remain the same regardless of backend:

```
POST   /api/upload                  - Upload & process IFC/JSON files
GET    /api/entityGuids             - Query entity GUIDs
GET    /api/componentGuids          - Query component GUIDs
GET    /api/components              - Retrieve component data
GET    /api/models                  - List all models
GET    /api/entityTypes             - List entity types
GET    /api/stores                  - List available data stores
POST   /api/refresh                 - Manually refresh memory tree
GET    /api/status                  - Server status
```

## Development Guide

### Adding a New Backend

To implement a new data store backend (e.g., PostgreSQL):

1. **Create backend folder:**
   ```
   dataStores/postgresqlBased/
   ├── __init__.py
   ├── postgresqlBased.py
   └── postgresqlMemoryTree.py
   ```

2. **Implement DataStore:**
   ```python
   # postgresqlBased.py
   class PostgreSQLStore:
       def __init__(self, connection_string=None):
           # Initialize database connection
           pass
       
       def store(self, filename, components):
           # Insert components into database
           pass
       
       # ... other methods ...
   ```

3. **Implement Memory Tree:**
   ```python
   # postgresqlMemoryTree.py
   class PostgreSQLMemoryTree:
       def __init__(self, store=None):
           # Initialize with store reference
           pass
       
       def get_entity_guids(self, models=None, entity_types=None, components=None):
           # Query database and return results
           pass
       
       # ... other methods ...
   ```

4. **Update server.py:**
   ```python
   def _initialize_backend(self):
       if self.data_store_type == 'postgresqlBased':
           from postgresqlBased import PostgreSQLStore
           from postgresqlMemoryTree import PostgreSQLMemoryTree
           
           self.file_store = PostgreSQLStore()
           self.memory_tree = PostgreSQLMemoryTree()
   ```

5. **Update startup prompt:**
   Add to `ifcxServerFileStore.py` in `get_data_store_type()` function

### Testing Different Backends

```bash
# Test file-based backend
python ifcxServerFileStore.py
# Choose 1

# Test MongoDB backend
python ifcxServerFileStore.py
# Choose 2 (will fail until MongoDB implementation complete)

# Direct test with environment variable
set IFC_DATA_STORE=fileBased
python server.py

# Run unit tests for each backend
python -m pytest tests/test_filebased_backend.py
python -m pytest tests/test_mongodb_backend.py
```

## Files to Remove (Legacy)

After migration is complete:
- `app.py` - Replaced by `server.py`
- `memoryTree.py` - Moved to `dataStores/fileBased/memoryTree.py`

**Keep for now** for compatibility, but reference the new locations in documentation.

## Summary of Changes

| Item | Old Location | New Location | Status |
|------|--------------|--------------|--------|
| Core Flask Server | `app.py` | `server.py` | Active |
| Startup Script | `ifcxServerFileStore.py` | `ifcxServerFileStore.py` | Updated |
| File-Based Store | `dataStores/fileBased/` | `dataStores/fileBased/` | Unchanged |
| Memory Tree (File-Based) | `memoryTree.py` (root) | `dataStores/fileBased/memoryTree.py` | Moved |
| MongoDB Store | N/A | `dataStores/mongodbBased/` | New (Stub) |
| MongoDB Memory Tree | N/A | `dataStores/mongodbBased/` | New (Stub) |

## Next Steps

1. **Test current structure** with file-based backend
2. **Verify API compatibility** - all endpoints should work as before
3. **Implement MongoDB backend** when needed
4. **Add more backends** following the pattern
5. **Add comprehensive tests** for backend abstraction layer

## Questions & Troubleshooting

### My existing imports are broken

Update from:
```python
from app import app
from memoryTree import MemoryTree
```

To:
```python
from server import create_app, IFCProcessingServer
from dataStores.fileBased import MemoryTree
```

### How do I know which backend is active?

```python
from server import IFCProcessingServer
server = IFCProcessingServer()
print(server.data_store_type)  # Shows 'fileBased' or 'mongodbBased'
```

Or check the `GET /api/status` endpoint response which includes `data_store` field.

### Can I switch backends at runtime?

Not directly - the backend is selected at server startup time via environment variable or server initialization. To switch backends, restart the server with the different configuration.

### What about existing MongoDB data?

Since MongoDB implementation is not complete, no existing MongoDB data exists. When implemented, migration tooling will be provided if needed.

---

**Last Updated:** 2024
**Version:** 0.1.0
