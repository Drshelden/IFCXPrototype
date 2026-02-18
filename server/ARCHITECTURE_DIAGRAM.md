# Project Reorganization - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      IFC Processing Server                          │
│              Reorganized with Pluggable Backends                    │
└─────────────────────────────────────────────────────────────────────┘

                            USER INTERACTION
                                  │
                        ┌─────────┴──────────┐
                        │                    │
                    CLI Start          Web Browser
                        │                    │
              ┌─────────┴────────┐          │
              │                  │          │
         Python CLI          Flask UI  (http://:5000)
              │                  │          │
              └────────┬─────────┴──────────┘
                       │
                       ▼
            ╔══════════════════════╗
            ║ ifcxServerFileStore  ║  ← Startup Script (Enhanced)
            ║      .py             ║  - Shows backend menu
            ║                      ║  - Sets environment variable
            ╚════════┬═════════════╝  - Launches server.py
                     │
          ┌──────────┴──────────┐
          │                     │
      [Backend Menu]     [Environment Variable]
      1. fileBased         set IFC_DATA_STORE
      2. mongodbBased
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
            ╔════════════════════════════════════╗
            ║        server.py (NEW!)            ║
            ║  Backend-Agnostic Core Server      ║
            ║                                    ║
            ║  class IFCProcessingServer:        ║
            ║    - __init__(backend_type)       ║
            ║    - _initialize_backend()        ║
            ║    - _register_routes()           ║
            ║                                    ║
            ║  def create_app(backend_type)     ║
            ╚════════════┬═════════════════════╘
                         │
             ┌───────────┼───────────┐
             │ Backend Selection      │
             └───┬─────────────────┬──┘
                 │                 │
    ┌────────────▼────────────┐   └──────────────┐
    │                          │                  │
    │                          ▼                  ▼
    │              ╔═══════════════════════╗   ╔════════════════╗
    │              ║ MongoDB Backend       ║   ║ File-Based     ║
    │              ║ (Stub - Future)       ║   ║ Backend        ║
    │              ╚═══════════════════════╝   ║ (✅ Active)    ║
    │              - MongoDBStore         │   ╚════════════════╝
    │              - MongoDBMemoryTree    │   - FileBasedStore
    │                                      │   - MemoryTree
    │                                      │
    │              Similar Pattern         │   Location:
    │              for PostgreSQL,          │   dataStores/
    │              Redis, etc.              │   fileBased/
    │                                      │
    └──────────────────────┬───────────────┘
                           │
                    ┌──────▼──────┐
                    │ All Backends │
                    │ Implement    │
                    │ Same         │
                    │ Interfaces   │
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                │ DataStore Interface │
                │ MemoryTree Interface│
                └─────────┬───────────┘
                          │
                ┌─────────┴──────────────┐
                │                        │
         ┌──────▼───────┐         ┌──────▼────────┐
         │ store()      │         │ refresh()     │
         │ retrieve()   │         │ get_entity... │
         │ list_dirs()  │         │ get_component │
         │              │         │ get_models()  │
         └──────┬───────┘         └──────┬────────┘
                │                        │
                └────────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │  Flask Routes   │
                    │  (Uniform API)  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    /api/upload      /api/components      /api/status
    /api/models      /api/entityGuids     /api/stores
    /api/refresh     /api/componentGuids  /api/entityTypes
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼──────────┐
                    │  API Response     │
                    │  (JSON Format)    │
                    └───────────────────┘
                             │
                    ┌────────▼──────────┐
                    │ Client/Consumer   │
                    │ (Web UI/API User) │
                    └───────────────────┘
```

## Backend Comparison

```
╔════════════════════════════════════════════════════════════════════╗
║                    Backend Comparison Matrix                       ║
╠════════════════════════════════════════════════════════════════════╣
║                   │ File-Based │ MongoDB    │ PostgreSQL (Planned) ║
║ Status           │ ✅ Active  │ 🔄 Stub    │ 📋 Planned          ║
║ Storage          │ Filesystem │ Clusters   │ Database             ║
║ Scalability      │ Good       │ Excellent  │ Excellent            ║
║ Query Speed      │ Fast       │ Very Fast  │ Very Fast            ║
║ Setup            │ None       │ Medium     │ Medium               ║
║ Development      │ ✅ Done    │ In Dev     │ Not Started          ║
║ Dependencies     │ Flask      │ pymongo    │ psycopg2             ║
║ Data Persistence │ Files      │ Database   │ Database             ║
║ Best For         │ Dev/Test   │ Production │ Enterprise           ║
╚════════════════════════════════════════════════════════════════════╝
```

## Project Structure

```
server/
│
├── 🆕 server.py                     ← Core Flask Server
│   │                                   (Backend selector & routes)
│   │
│   ├── class IFCProcessingServer
│   │   ├── __init__(backend_type)
│   │   ├── _configure_app()
│   │   ├── _initialize_backend()
│   │   ├── _register_routes()
│   │   └── _refresh_memory_tree()
│   │
│   └── def create_app(backend_type)
│       └── Returns Flask app instance
│
├── 📝 ifcxServerFileStore.py        ← Startup Script (Updated)
│   │                                   (Backend selection menu)
│   └── get_data_store_type()        ← User prompt
│
├── 📁 dataStores/
│   │
│   ├── 📁 fileBased/                ← File-Based Backend
│   │   ├── __init__.py              ← Package exports
│   │   ├── fileBased.py             ← FileBasedStore class
│   │   ├── memoryTree.py            ← MemoryTree class (MOVED)
│   │   │   │
│   │   │   ├── class MemoryTree
│   │   │   │   ├── refresh_from_store()
│   │   │   │   ├── get_entity_guids()
│   │   │   │   ├── get_component_guids()
│   │   │   │   ├── get_components()
│   │   │   │   ├── get_models()
│   │   │   │   └── get_entity_types()
│   │   │   │
│   │   │   └── Query Indexing
│   │   │       ├── by_entity
│   │   │       ├── by_type
│   │   │       ├── by_entityType
│   │   │       ├── by_componentGuid
│   │   │       └── entity_types
│   │   │
│   │   └── 📁 data/                 ← Component Storage
│   │       ├── ModelName1/
│   │       │   ├── entityGuid_componentGuid.json
│   │       │   └── ...
│   │       ├── ModelName2/
│   │       │   ├── entityGuid_componentGuid.json
│   │       │   └── ...
│   │       └── ...
│   │
│   └── 📁 mongodbBased/            ← MongoDB Backend (NEW)
│       ├── __init__.py             ← Package exports
│       ├── mongodbBased.py         ← MongoDBStore (Stub)
│       │   ├── class MongoDBStore
│       │   ├── class MongoDBStoreConfig
│       │   └── Placeholder methods
│       │
│       └── mongodbMemoryTree.py    ← MongoDBMemoryTree (Stub)
│           ├── class MongoDBMemoryTree
│           ├── class MongoDBMemoryTreeConfig
│           └── Placeholder methods
│
├── 📁 ingestors/
│   ├── ifc4ingestor.py             ← IFC to JSON converter
│   └── utils.py                    ← Helper utilities
│
├── 📁 utils/
│   ├── generate_ifc_hierarchy.py   ← Generate IFC class tree
│   ├── generate_ifc_flat.py        ← Flat class list
│   └── [IFC schema analysis tools]
│
├── 📁 examples/                    ← NEW: Usage Examples
│   ├── README.md                   ← Examples guide
│   └── example_usage.py            ← Code examples
│
├── 📁 docs/                        ← Documentation
│   ├── API_DOCUMENTATION.md
│   ├── API_QUICK_REFERENCE.md
│   └── [Other docs]
│
├── 📚 QUICK_START.md               ← Start here! (Getting started)
├── 📚 REORGANIZATION.md            ← Architecture details
├── 📚 BACKEND_INTERFACE.md         ← How to add backends
├── 📚 PROJECT_REORGANIZATION.md    ← Summary of changes
├── 📚 VERIFICATION_CHECKLIST.md    ← Test the setup
└── 📚 DOCUMENTATION_INDEX.md       ← Navigate all docs
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Upload IFC File                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   IFC Ingestor  │
                    │  ifc4ingestor.py│
                    │                 │
                    │  IFC → JSON     │
                    └────────┬────────┘
                             │
                    ┌────────▼──────────────┐
                    │  Normalized JSON     │
                    │  {componentGuid, ... │
                    │   entityGuid, ...}   │
                    └────────┬──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   File-Based          MongoDB              PostgreSQL
   (Active)            (Stub)               (Future)
        │                    │                    │
        │         ┌──────────┴──────────┐        │
        │         │                     │        │
        ▼         ▼                     ▼        ▼
    Store:    NotImplemented        Store:      Store:
    · Save    (to implement)        · Insert    · Insert
    · Index                         · Index     · Index
    · Cache                         · Cache     · Cache
        │                            │          │
        ▼                            ▼          ▼
    MemoryTree             MemoryTree        MemoryTree
    Indexing:              MongoDB           PostgreSQL
    · by_entity            Queries:          Queries:
    · by_type              · Aggregation     · SQL
    · by_entityType        · Projection      · ACID
    · by_componentGuid     · Indexing        · Join
        │                    │                 │
        │         ┌──────────┼─────────┐      │
        │         │          │         │      │
        └─────────┼──────────┼─────────┼──────┘
                  │          │         │
                  ▼          ▼         ▼
            ┌───────────────────────────────┐
            │  Uniform Query Interface      │
            │  (Same for all backends)      │
            ├───────────────────────────────┤
            │ get_entity_guids()            │
            │ get_component_guids()         │
            │ get_components()              │
            │ get_models()                  │
            │ get_entity_types()            │
            │ refresh()                     │
            └───────────┬───────────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │   Flask REST API        │
            │ /api/components...      │
            │ /api/entityGuids...     │
            │ /api/models...          │
            │ /api/status...          │
            └────────────┬────────────┘
                         │
                    ┌────┴─────┐
                    │           │
                    ▼           ▼
                Web UI      API Client
                (Admin)    (Python/CURL)
```

## Configuration Flow

```
Configuration Priority (First to Last):
┌────────────────────────────────────────────────┐
│ 1. Command-line argument (if supported)       │
│ 2. Environment variable: IFC_DATA_STORE        │
│ 3. User prompt (interactive selection)        │
│ 4. Default value: fileBased                   │
└────────────────────────────────────────────────┘

Environment Variable Usage:
┌────────────────────────────────────────────────┐
│ set IFC_DATA_STORE=fileBased    # Default     │
│ set IFC_DATA_STORE=mongodbBased  # Future     │
│ set IFC_DATA_STORE=postgresqlBased # Future   │
└────────────────────────────────────────────────┘

Programmatic Usage:
┌────────────────────────────────────────────────┐
│ from server import IFCProcessingServer        │
│ server = IFCProcessingServer('fileBased')     │
│ # or                                           │
│ app = create_app(data_store_type='fileBased')│
└────────────────────────────────────────────────┘
```

## Data Model

```
Component (JSON)
├── componentGuid (unique identifier)
├── entityGuid (parent entity)
├── componentType (e.g., WallComponent)
├── entityType (e.g., IfcWall)
└── [other properties preserved from IFC]

Model (Collection of Components)
├── name (model identifier)
├── components[] (array of component objects)
├── created_at (timestamp)
└── metadata...

Entity (Abstract)
├── entityGuid
├── entityType
└── components[] (components for this entity)
```

## API Endpoint Flow

```
Request: GET /api/components?models=House&entityTypes=IfcWall
    │
    ▼
Memory Tree Query: get_component_guids()
    │
    ├─→ Filter by models: ['House']
    ├─→ Filter by entityTypes: ['IfcWall']
    └─→ Return: [component_guid_1, component_guid_2, ...]
    │
    ▼
Memory Tree Query: get_components()
    │
    ├─→ Find each component by GUID
    ├─→ Organize by model
    └─→ Return: {House: [{component1}, {component2}]}
    │
    ▼
Flask Response (JSON)
    │
    └─→ Content-Type: application/json
        {
            "House": [
                {componentGuid, entityGuid, componentType, ...},
                {componentGuid, entityGuid, componentType, ...}
            ]
        }
```

## Scalability Path

```
Current State (File-Based)
        ↓
Optimize Memory Tree Indexing
        ↓
Add File-Based Caching Layer
        ↓
Implement MongoDB Backend
        ↓
MongoDB with Redis Cache
        ↓
PostgreSQL with Redis Cache
        ↓
Distributed Backend Selection
        ↓
Advanced Sharding & Replication
```

---

**Legend:**
- 🆕 = New file/feature
- 📝 = Modified file
- 📁 = Directory
- ✅ = Complete/Working
- 🔄 = In progress/Stub
- 📋 = Planned future

**Version**: 0.1.0 (File-Based Active, MongoDB Stub Ready)
