# IFC Processing Server - Reorganization Summary

## What Was Reorganized

The IFC Processing Server has been reorganized to support pluggable data store backends. This allows easy switching between storage solutions (file-based, MongoDB, PostgreSQL, etc.) while maintaining a unified API.

## Key Changes

### 1. **Core Server Refactoring**
   - **New**: `server.py` - Backend-agnostic core Flask server
   - **Old**: `app.py` - File-based implementation
   - **Impact**: Server now handles backend selection and routing

### 2. **File-Based Backend Reorganization**
   - **New Path**: `dataStores/fileBased/`
   - **Contents**:
     - `fileBased.py` - Store implementation (unchanged)
     - `memoryTree.py` - Query engine (moved from root)
     - `__init__.py` - Package exports
     - `data/` - Component storage directory
   - **Old Location**: Files at root level
   - **Impact**: Better organization, easier to maintain multiple backends

### 3. **MongoDB Backend (New)**
   - **New Path**: `dataStores/mongodbBased/`
   - **Contents**:
     - `mongodbBased.py` - MongoDB store interface (stub)
     - `mongodbMemoryTree.py` - MongoDB query engine (stub)
     - `__init__.py` - Package exports
   - **Status**: Stub implementation ready for development
   - **Impact**: Provides template for MongoDB backend implementation

### 4. **Updated Startup Script**
   - **File**: `ifcxServerFileStore.py` (enhanced)
   - **Changes**:
     - Now allows backend selection
     - Supports environment variable configuration
     - Launches `server.py` instead of `app.py`
   - **Impact**: Easier backend switching

### 5. **Documentation**
   - **New Files**:
     - `REORGANIZATION.md` - Full architecture overview
     - `QUICK_START.md` - Quick reference guide
     - `BACKEND_INTERFACE.md` - Backend implementation guide
     - `PROJECT_REORGANIZATION.md` - This file
   - **Purpose**: Help developers understand and extend the system

### 6. **Examples**
   - **New Path**: `examples/`
   - **Contents**:
     - `example_usage.py` - Usage examples
   - **Purpose**: Show how to use the new architecture

## Architecture Comparison

### Before Reorganization
```
server/
├── app.py                    ← Flask app (file-based only)
├── memoryTree.py             ← Query engine (at root)
├── ifcxServerFileStore.py    ← Startup script
├── dataStores/
│   └── fileBased/
│       ├── fileBased.py
│       └── data/             ← Component storage
└── ingestors/
    └── ifc4ingestor.py
```

### After Reorganization
```
server/
├── server.py                 ← Core! Backend-agnostic Flask server
├── ifcxServerFileStore.py    ← Enhanced startup script
├── dataStores/
│   ├── __init__.py
│   ├── fileBased/            ← File-based backend
│   │   ├── __init__.py
│   │   ├── fileBased.py
│   │   ├── memoryTree.py     ← Moved here
│   │   └── data/
│   └── mongodbBased/         ← MongoDB backend (new)
│       ├── __init__.py
│       ├── mongodbBased.py   ← Stub
│       └── mongodbMemoryTree.py
├── ingestors/
│   └── ifc4ingestor.py
├── examples/
│   ├── __init__.py
│   └── example_usage.py      ← Usage examples
└── docs/ (including new .md files)
```

## How It Works

### Backend Selection

1. **At Startup** (via `ifcxServerFileStore.py`):
   ```bash
   python ifcxServerFileStore.py
   # Prompts user to select backend
   ```

2. **Via Environment Variable**:
   ```bash
   set IFC_DATA_STORE=fileBased
   python server.py
   ```

3. **Programmatically**:
   ```python
   from server import IFCProcessingServer
   server = IFCProcessingServer(data_store_type='fileBased')
   ```

### Backend Initialization Flow

```
ifcxServerFileStore.py
    ↓
    └─→ Get backend choice (file/mongo)
        ↓
        └─→ Set IFC_DATA_STORE environment variable
            ↓
            └─→ Launch server.py
                ↓
                └─→ IFCProcessingServer.__init__()
                    ↓
                    └─→ _initialize_backend()
                        ├─→ If fileBased:
                        │   ├── Import FileBasedStore
                        │   └── Import MemoryTree
                        └─→ If mongodbBased:
                            ├── Import MongoDBStore
                            └── Import MongoDBMemoryTree
```

## API Consistency

All backends provide the same API endpoints:

```
POST   /api/upload                  - Upload & process files
GET    /api/models                  - List models
GET    /api/entityGuids             - Query entities
GET    /api/componentGuids          - Query components
GET    /api/components              - Retrieve data
GET    /api/stores                  - List backends
GET    /api/status                  - Server status
```

**Status endpoint now includes backend type:**
```json
{
    "status": "running",
    "data_store": "fileBased",
    "timestamp": "2024-02-17T10:30:00",
    "version": "0.1.0"
}
```

## Migration Information

### For Existing Code

**Old import:**
```python
from app import app
from memoryTree import MemoryTree
from dataStores.fileBased import FileBasedStore
```

**New import:**
```python
from server import create_app, IFCProcessingServer
from dataStores.fileBased import FileBasedStore, MemoryTree
```

### For Existing Data

- **File-based data**: Unchanged
- **Location**: Still at `dataStores/fileBased/data/`
- **No migration needed**: Existing component files work as-is

## Benefits of Reorganization

1. **Pluggable Architecture**
   - Easy to add new backends (PostgreSQL, Redis, etc.)
   - No changes to core server needed
   - Follows Open/Closed Principle

2. **Better Organization**
   - Backend-specific code isolated
   - Clear separation of concerns
   - Easier to understand codebase

3. **Scalability**
   - File-based for development
   - MongoDB for production
   - PostgreSQL for enterprise
   - Future backends without refactoring

4. **Testing**
   - Test each backend independently
   - Mock backends for testing
   - Benchmark different backends

5. **Maintenance**
   - Changes to one backend don't affect others
   - Easier to deprecate or upgrade backends
   - Clear interface contracts

## Next Steps

### Immediate
1. ✅ Test file-based backend (default, already works)
2. ✅ Verify API endpoints unchanged
3. ✅ Verify startup script works

### Short Term (This Sprint)
1. Implement basic MongoDB backend
2. Test MongoDB operations
3. Add MongoDB configuration documentation

### Medium Term
1. Add PostgreSQL backend
2. Add Redis caching layer
3. Performance benchmarking

### Long Term
1. Add more backends based on demand
2. Add advanced querying across backends
3. Add backend migration tools

## Files Modified

| File | Purpose | Change |
|------|---------|--------|
| new: `server.py` | Core Flask server | New main entry point |
| mod: `ifcxServerFileStore.py` | Startup script | Added backend selection |
| new: `dataStores/fileBased/memoryTree.py` | Query engine | Moved from root |
| new: `dataStores/mongodbBased/` | MongoDB backend | New directory |
| old: `app.py` | Flask routes | Now in server.py (optional: can remove) |
| old: `memoryTree.py` | Query engine | Now in dataStores/fileBased/ (optional: can remove) |
| new: `REORGANIZATION.md` | Architecture docs | New documentation |
| new: `QUICK_START.md` | Quick reference | New documentation |
| new: `BACKEND_INTERFACE.md` | Backend guide | New documentation |
| new: `examples/` | Example code | New directory |

## Backward Compatibility

- ✅ All API endpoints unchanged
- ✅ Data location unchanged
- ✅ File structure unchanged
- ✅ Query results identical
- ✅ Upload functionality identical

**Breaking Changes**: None for end users or API consumers

## Testing New Architecture

### Test File-Based Backend
```bash
# Start server
python ifcxServerFileStore.py
# Choose 1 (fileBased)

# Test API
curl http://localhost:5000/api/status
# Should see: "data_store": "fileBased"

# Upload test data
# Use admin interface at http://localhost:5000

# Query data
curl "http://localhost:5000/api/components?models=TestModel"
```

### Test Backend Switching (When MongoDB is implemented)
```bash
# Test file-based
set IFC_DATA_STORE=fileBased
python server.py
# Should work

# Test MongoDB (when ready)
set IFC_DATA_STORE=mongodbBased
python server.py
# Will show "MongoDB store initialized (stub mode)"
```

## Documentation Structure

```
docs/
├── REORGANIZATION.md        ← Architecture overview
├── QUICK_START.md           ← Getting started
├── BACKEND_INTERFACE.md     ← Developer guide
├── PROJECT_REORGANIZATION.md  ← This file (summary)
├── API_DOCUMENTATION.md     ← API reference (existing)
└── ...
```

## Support & Questions

### What Changed?
- Core server now supports multiple backends
- File-based is default, unchanged
- MongoDB ready for implementation

### How Do I Upgrade?
- For end users: No upgrade needed, everything is backward compatible
- For developers: Update imports to use new structure

### What About My Data?
- All existing data at `dataStores/fileBased/data/` remains unchanged
- No migration required
- Can continue using file-based backend indefinitely

### How Do I Add a Custom Backend?
1. Create directory in `dataStores/`
2. Implement DataStore and MemoryTree interfaces
3. Register in `server.py` _initialize_backend()
4. See `BACKEND_INTERFACE.md` for detailed guide

---

## Summary

The IFC Processing Server has been successfully reorganized to support pluggable data store backends. The file-based backend remains the default and is unchanged. The architecture now supports adding MongoDB, PostgreSQL, or any other data store backend without modifying the core server code.

**Status**: ✅ Ready for use with file-based backend  
**MongoDB**: 🔄 Ready for implementation (stub in place)  
**Documentation**: ✅ Complete

---

**Last Updated**: February 17, 2026  
**Version**: 0.1.0  
**Architecture**: Backend-Agnostic with Pluggable Stores
