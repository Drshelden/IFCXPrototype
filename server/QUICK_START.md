# IFC Processing Server - Quick Start

## Starting the Server

### Basic Usage
```bash
# Default: file-based backend on port 5000
python server.py
```

### With Options
```bash
# Specify file-based backend explicitly
python server.py --backend fileBased

# MongoDB backend (when implemented)
python server.py --backend mongodbBased

# Custom port
python server.py --port 5001

# Debug mode (enables auto-reload, detailed errors)
python server.py --debug

# Custom host and port
python server.py --host 127.0.0.1 --port 8080

# Show all available options
python server.py --help
```

### Using Environment Variables (Legacy)
```bash
# Set default backend before running
set IFC_DATA_STORE=fileBased
python server.py              # Uses fileBased backend

# Or pass via command line (takes precedence)
python server.py --backend mongodbBased
```

## Current Data Store Backends

### File-Based (✅ Active)
- **Status**: Fully functional
- **Storage**: JSON files in `dataStores/fileBased/data/`
- **Models**: Each model stored in its own directory
- **Components**: Individual JSON files per component
- **Memory**: Loads into MemoryTree for fast queries
- **Use Case**: Development, testing, debugging

### MongoDB (🔄 In Development)
- **Status**: Stub implementation
- **Connection**: Requires MongoDB server
- **Storage**: MongoDB collections
- **Features**: Indexing, aggregation, scaling
- **Use Case**: Production, large datasets (when implemented)

## Project Structure

```
server/
├── server.py                    ← Core Flask server (entry point)
├── dataStores/
│   ├── fileBased/              ← File-based backend
│   │   ├── fileBased.py
│   │   ├── memoryTree.py
│   │   └── data/              ← Component storage
│   └── mongodbBased/           ← MongoDB backend (stub)
│       ├── mongodbBased.py
│       └── mongodbMemoryTree.py
├── ingestors/
│   └── ifc4ingestor.py        ← IFC to JSON converter
├── utils/                      ← IFC schema utilities
├── templates/                  ← HTML templates
└── docs/
    └── REORGANIZATION.md       ← Full architecture docs
```

## Using the Server

### Running with File-Based Backend

```bash
# 1. Start the server
python ifcxServerFileStore.py
# Select option 1 for file-based

# 2. Open admin interface
http://localhost:5000

# 3. Upload IFC or JSON files
# Files will be stored in dataStores/fileBased/data/

# 4. Query via API
curl "http://localhost:5000/api/models"
curl "http://localhost:5000/api/components?models=ModelName"
```

### File Organization

When you upload a model named `MyModel.ifc`:

```
dataStores/fileBased/data/
└── MyModel/
    ├── 0d68ad35-29c7-484d-907c-65a3fbc0eadb_5d7be3a6-fe8b-0924-729b-33cd0f175b6a.json
    ├── 0d68ad35-29c7-484d-907c-65a3fbc0eadb_70c8c03a-adc2-63f9-182c-1b24c6de3200.json
    └── ... (one file per component)
```

## API Endpoints

### Models & Components
```
GET  /api/models                  → List all loaded models
POST /api/upload                  → Upload and process IFC/JSON
GET  /api/components              → Query component data
GET  /api/entityGuids             → Query entity GUIDs
GET  /api/componentGuids          → Query component GUIDs
GET  /api/entityTypes             → List entity types
```

### System
```
GET  /api/status                  → Server status (includes data_store type)
GET  /api/stores                  → Available data stores
POST /api/refresh                 → Refresh memory tree
```

## Switching Backends

### To Change Backends

1. **Stop the running server** (Ctrl+C)
2. **Start with new backend:**
   ```bash
   set IFC_DATA_STORE=mongodbBased
   python server.py
   ```
3. **Or use interactive mode:**
   ```bash
   python ifcxServerFileStore.py
   # Choose different option
   ```

## Environment Variables

```bash
# Select backend
set IFC_DATA_STORE=fileBased        # ✅ Works now
set IFC_DATA_STORE=mongodbBased     # 🔄 In development

# Server settings
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000
```

## Backend Switching Example

```bash
# Start with file-based
python ifcxServerFileStore.py
# Choose 1

# In another terminal, test
curl http://localhost:5000/api/status
# Response includes: "data_store": "fileBased"

# Stop the server (Ctrl+C)
# Restart with MongoDB (when available)
set IFC_DATA_STORE=mongodbBased
python server.py
```

## Troubleshooting

### Port Already in Use
```bash
# Change port when starting
set FLASK_PORT=5001
python server.py
```

### Import Errors
```bash
# Ensure you're in project directory with virtual environment
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

### Files Not Found
```bash
# Make sure working directory is the server root
cd c:\_LOCAL\GitHub\IFCXPrototype\server
python ifcxServerFileStore.py
```

## Data Store Comparison

| Feature | File-Based | MongoDB |
|---------|-----------|---------|
| **Status** | ✅ Active | 🔄 Stub |
| **Storage** | Local filesystem | Remote DB |
| **Speed** | Fast (local) | Fast (indexed) |
| **Scalability** | Good | Excellent |
| **Setup** | None | Requires MongoDB |
| **Use Case** | Dev/Test | Production |
| **Data Persistence** | Permanent files | Database |
| **Query Speed** | In-memory | Indexed queries |

## Next Steps

1. **Upload a model** via the admin interface at http://localhost:5000
2. **Query components** using the API
3. **Review data structure** in `dataStores/fileBased/data/`
4. **Implement MongoDB** backend when needed

## Documentation

For detailed architecture information, see [REORGANIZATION.md](./REORGANIZATION.md)

## Common Commands

```bash
# Start with file-based (default)
python ifcxServerFileStore.py

# Start directly
python server.py

# Test server status
curl http://localhost:5000/api/status

# List all models
curl http://localhost:5000/api/models

# List available stores
curl http://localhost:5000/api/stores

# Get components from a model
curl "http://localhost:5000/api/components?models=MyModel"
```

---

**Quick Links:**
- Admin Interface: http://localhost:5000
- Viewer: http://localhost:5000/viewer
- API Status: http://localhost:5000/api/status
- Architecture: [REORGANIZATION.md](./REORGANIZATION.md)
