# IFC Processing Server - Documentation Index

## 🚀 Quick Navigation

### I want to...

| Goal | Document |
|------|----------|
| **Start the server** | [QUICK_START.md](QUICK_START.md) |
| **Understand the architecture** | [REORGANIZATION.md](REORGANIZATION.md) |
| **Implement a new backend** | [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md) |
| **See code examples** | [examples/example_usage.py](examples/example_usage.py) or [examples/README.md](examples/README.md) |
| **Verify reorganization works** | [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) |
| **Get a summary of changes** | [PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md) |
| **Use the API** | [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) |
| **Understand IFC schema** | [utils/README_IFC_SCRIPTS.md](utils/README_IFC_SCRIPTS.md) |

## 📚 Documentation Structure

```
Documentation/
├── QUICK_START.md              ← START HERE for quick setup
├── REORGANIZATION.md           ← Full architecture details
├── BACKEND_INTERFACE.md        ← How to add new backends
├── PROJECT_REORGANIZATION.md   ← Summary of changes
├── VERIFICATION_CHECKLIST.md   ← Test the setup
├── DOCUMENTATION_INDEX.md      ← This file (navigation)
│
├── docs/
│   ├── API_DOCUMENTATION.md    ← API reference (original)
│   ├── API_QUICK_REFERENCE.md  ← API quick ref (original)
│   └── ...
│
├── utils/
│   ├── README_IFC_SCRIPTS.md   ← IFC utilities docs
│   └── ...
│
└── examples/
    ├── README.md               ← Examples guide
    └── example_usage.py        ← Code examples
```

## 🏗️ Architecture Overview

### New Project Structure
```
server/
├── server.py                   ← Core Flask server (NEW - backend selector)
├── ifcxServerFileStore.py      ← Startup script (UPDATED - with backend menu)
├── dataStores/
│   ├── fileBased/
│   │   ├── fileBased.py       ← File store
│   │   ├── memoryTree.py      ← Query engine (MOVED from root)
│   │   ├── __init__.py        ← Package exports
│   │   └── data/              ← Component storage
│   └── mongodbBased/          ← MongoDB backend (NEW - stub)
│       ├── mongodbBased.py
│       ├── mongodbMemoryTree.py
│       └── __init__.py
├── ingestors/
│   └── ifc4ingestor.py        ← IFC to JSON converter
└── docs/ & utils/             ← Documentation
```

### Backend Workflow
```
User Request
    ↓
ifcxServerFileStore.py (startup)
    ↓
Server Selection (file/mongo)
    ↓ (set IFC_DATA_STORE)
↓
server.py (core)
    ↓
IFCProcessingServer class
    ↓
_initialize_backend()
    ├─→ fileBased: FileBasedStore + MemoryTree
    └─→ mongodbBased: MongoDBStore + MongoDBMemoryTree
    ↓
Flask Routes (same for all backends)
    ↓
API Endpoints (consistent interface)
```

## 🔧 Common Tasks

### Start the Server

**File-Based (Default):**
```bash
python ifcxServerFileStore.py
# Select option 1
# or
python server.py
```

**MongoDB (When Ready):**
```bash
set IFC_DATA_STORE=mongodbBased
python server.py
```

See [QUICK_START.md](QUICK_START.md) for details.

### Add a New Backend

1. Create `dataStores/newBackend/` directory
2. Implement DataStore interface (4 methods)
3. Implement MemoryTree interface (6 methods)
4. Register in `server.py`
5. Test and document

See [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md) for full guide.

### Query Components

```python
from server import IFCProcessingServer

server = IFCProcessingServer('fileBased')
tree = server.memory_tree

# Get entity GUIDs
entities = tree.get_entity_guids(models=['Model1'])

# Get component GUIDs
components = tree.get_component_guids(models=['Model1'])

# Get component data
data = tree.get_components(components)
```

See [examples/README.md](examples/README.md) for more.

### Test the Setup

Run verification checklist:
```bash
# Check directory structure
# Verify startup works
# Test API endpoints
# Confirm backends work
```

See [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md).

## 🎯 Key Concepts

### Backend Interface
Both backends must implement:
- **DataStore**: store(), retrieve(), list_directories()
- **MemoryTree**: get_entity_guids(), get_component_guids(), get_components(), get_models(), get_entity_types(), refresh()

### API Consistency
All backends provide identical API endpoints:
- `/api/upload` - Upload files
- `/api/components` - Get component data
- `/api/models` - List models
- `/api/status` - Server status (includes backend type)
- etc.

### Configuration
Select backend via:
1. **Environment Variable**: `IFC_DATA_STORE=fileBased`
2. **Startup Menu**: Run `ifcxServerFileStore.py`, choose option
3. **Programmatically**: `IFCProcessingServer(data_store_type='fileBased')`

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **File-Based Backend** | ✅ Active | Fully functional, ready to use |
| **MongoDB Backend** | 🔄 Stub | Interface ready, implementation pending |
| **Core Server** | ✅ Complete | Backend-agnostic, all routes working |
| **Startup Script** | ✅ Updated | Now supports backend selection |
| **Documentation** | ✅ Complete | Comprehensive guides provided |
| **Examples** | ✅ Provided | Usage examples included |
| **Testing** | ✅ Checklist | Verification guide provided |

## 🗺️ Document Quick Reference

### For Users
- **[QUICK_START.md](QUICK_START.md)** - Get server running in 5 minutes
- **[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Use the API
- **[examples/README.md](examples/README.md)** - See usage examples

### For Developers
- **[REORGANIZATION.md](REORGANIZATION.md)** - Understand the full architecture
- **[BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)** - Add new backends
- **[PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md)** - What changed and why
- **[VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)** - Test your setup

### For DevOps/Operations
- **[QUICK_START.md](QUICK_START.md)** - Deployment commands
- **[REORGANIZATION.md](REORGANIZATION.md#environment-variables)** - Configuration
- **[PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md#migration-information)** - Migration guide

### For Data Scientists/Researchers
- **[examples/example_usage.py](examples/example_usage.py)** - Code examples
- **[QUICK_START.md](QUICK_START.md#api-endpoints)** - Available endpoints
- **[utils/README_IFC_SCRIPTS.md](utils/README_IFC_SCRIPTS.md)** - IFC analysis tools

## 🔍 Looking for...?

### API Reference
- Quick: [docs/API_QUICK_REFERENCE.md](docs/API_QUICK_REFERENCE.md)
- Detailed: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- Examples: [examples/README.md](examples/README.md)

### Architecture Details
- Overview: [REORGANIZATION.md](REORGANIZATION.md)
- Changes: [PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md)
- Interfaces: [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)

### How to...
- Start server: [QUICK_START.md](QUICK_START.md)
- Use API: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- Add backend: [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)
- Query components: [examples/README.md](examples/README.md)
- Troubleshoot: [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)

### IFC-Specific
- Schema analysis: [utils/README_IFC_SCRIPTS.md](utils/README_IFC_SCRIPTS.md)
- Class hierarchy: [utils/IFC_Classes.json](utils/IFC_Classes.json)
- Entity lookup: [utils/IFC_Classes_Flat.json](utils/IFC_Classes_Flat.json)

## 📋 Checklists & Verification

- **Setup Verification**: [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) - 30 min verification
- **API Testing**: Use `curl` examples in [QUICK_START.md](QUICK_START.md)
- **Backend Testing**: See [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md#testing-your-backend)

## 🚦 Getting Started Quickly

### 1. New Users (5 min)
1. Read: [QUICK_START.md](QUICK_START.md)
2. Run: `python ifcxServerFileStore.py`
3. Visit: http://localhost:5000

### 2. Developers (15 min)
1. Read: [QUICK_START.md](QUICK_START.md)
2. Read: [PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md)
3. Review: [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)
4. Run: `python examples/example_usage.py`

### 3. Operations (10 min)
1. Read: [QUICK_START.md](QUICK_START.md)
2. Check: [REORGANIZATION.md](REORGANIZATION.md#environment-variables)
3. Verify: [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)

### 4. Researchers (20 min)
1. Read: [QUICK_START.md](QUICK_START.md)
2. Review: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
3. Study: [examples/example_usage.py](examples/example_usage.py)
4. Explore: [utils/README_IFC_SCRIPTS.md](utils/README_IFC_SCRIPTS.md)

## 📞 Support & Questions

| Question | Answer |
|----------|--------|
| How do I start the server? | [QUICK_START.md](QUICK_START.md) |
| How do I use the API? | [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) |
| How do I switch backends? | [QUICK_START.md](QUICK_START.md#switching-backends) |
| How do I add a backend? | [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md) |
| What changed? | [PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md) |
| Is my setup correct? | [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) |
| Show me examples | [examples/README.md](examples/README.md) |
| What's the architecture? | [REORGANIZATION.md](REORGANIZATION.md) |

## 📈 Roadmap

### ✅ Completed
- File-based backend (fully functional)
- Backend abstraction layer
- MongoDB stub implementation
- Comprehensive documentation
- Examples and verification checklist

### 🔄 In Progress
- MongoDB backend implementation
- Performance optimization
- Additional test coverage

### 📅 Planned
- PostgreSQL backend
- Redis caching layer
- Advanced querying
- Batch operations
- Migration tools

## 📄 All Documentation Files

Root Level:
- [QUICK_START.md](QUICK_START.md)
- [REORGANIZATION.md](REORGANIZATION.md)
- [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)
- [PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md)
- [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) ← You are here

In `docs/`:
- [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- [docs/API_QUICK_REFERENCE.md](docs/API_QUICK_REFERENCE.md)
- [docs/VIEWER_GUIDE.md](docs/VIEWER_GUIDE.md)
- And others...

In `utils/`:
- [utils/README_IFC_SCRIPTS.md](utils/README_IFC_SCRIPTS.md)
- Generated JSON files for IFC schema

In `examples/`:
- [examples/README.md](examples/README.md)
- [examples/example_usage.py](examples/example_usage.py)

## 🎓 Learning Path

**Complete Beginner** → [QUICK_START.md](QUICK_START.md)
    ↓
**Want to Understand Architecture** → [REORGANIZATION.md](REORGANIZATION.md)
    ↓
**Want to Extend/Add Backend** → [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)
    ↓
**Want to See Code Examples** → [examples/](examples/)
    ↓
**Want to Verify Setup** → [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)

## 🔗 Cross-References

- Start here for any topic: See table in "I want to..." section above
- API questions: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- Architecture questions: [REORGANIZATION.md](REORGANIZATION.md)
- Development questions: [BACKEND_INTERFACE.md](BACKEND_INTERFACE.md)
- Troubleshooting: [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)

---

**Version**: 0.1.0  
**Last Updated**: February 17, 2026  
**Status**: ✅ Ready for Use (File-Based) | 🔄 MongoDB Coming Soon

**Start here**: [QUICK_START.md](QUICK_START.md) ← Click to get started!
