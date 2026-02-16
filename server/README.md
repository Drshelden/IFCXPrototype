# IFC Processing Server

A headless Flask server for processing IFC (Industry Foundation Classes) files with a web-based admin interface.

## Features

- **Web Admin Interface** - Upload and process IFC files through a modern web UI
- **IFC to JSON Conversion** - Automatic conversion of IFC files to JSON components
- **File-Based Data Store** - Components stored in organized directory structure
- **In-Memory Component Tree** - Fast querying of components across models
- **RESTful API** - Upload, process, query and retrieve data through API endpoints
- **Drag & Drop Upload** - Intuitive file upload interface

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

**Option A: From Terminal**
```bash
python app.py
```

**Option B: From VS Code**
- Press `F5` or go to Run → Start Debugging
- Select "Flask Server" from the configuration dropdown

### 3. Access the Admin Panel

Open your browser and navigate to:
```
http://localhost:5000
```

### 4. (Optional) Use the Advanced Viewer

For advanced data exploration with 3D visualization:
```
http://localhost:5000/viewer
```

**📖 See [VIEWER_GUIDE.md](VIEWER_GUIDE.md) for detailed viewer documentation**

## File Structure

```
server/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── templates/
│   ├── admin.html                 # Web admin interface
│   └── viewer.html                # Advanced 3D viewer interface
├── ingestors/
│   ├── ifc4ingestor.py           # IFC to JSON converter
│   └── utils.py                   # Utility functions
├── dataStores/
│   └── fileBased.py              # File-based storage implementation
├── uploads/                       # Temporary upload storage
└── dataStores/fileBased/data/     # Processed component storage
```

## API Endpoints

### Upload & Process
- **POST** `/api/upload` - Upload and process IFC or JSON file
  - Form data: `file` (IFC or JSON file)
  - Returns: JSON with processing results

### Querying
- **GET** `/api/entities` - Query for entity GUIDs by filters
- **GET** `/api/guids` - Query for component GUIDs by filters
- **GET** `/api/components` - Retrieve component data by GUIDs
- **GET** `/api/models` - List all loaded models
- **GET** `/api/entity_types` - List all entity types

### Management
- **POST** `/api/refresh` - Manually refresh the memory tree
- **GET** `/api/status` - Get server status

**📖 For complete API documentation see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

## Architecture

### Three-Tier Storage

1. **Disk Storage** - Components stored as individual JSON files
2. **File-Based Data Store** - Manages disk organization by model and component
3. **Memory Tree** - In-memory index for fast querying

### Memory Tree Structure

The server loads all components into an organized tree structure for efficient querying:

```
Models:
├── HelloWall
│   ├── by_entity:    { entityGuid → [componentGuids] }
│   ├── by_type:      { componentType → [componentGuids] }
│   └── by_guid:      { componentGuid → componentData }
```

This enables:
- **O(1)** component lookup by GUID
- **Fast filtering** by entity or type across models
- **Real-time** query responses
- **Memory-efficient** storage with indexed references

The memory tree is refreshed on:
- Server startup
- File upload completion
- Manual `/api/refresh` request

1. **IFC Files**: Automatically converted to JSON components
2. **JSON Files**: Stored directly if they contain an array of components
3. **Storage**: Components stored in `dataStores/fileBased/data/<filename>/`
4. **Naming**: Each component saved as `<entityGuid>_<guid>.json`

### Example Directory Structure

```
dataStores/fileBased/data/
└── HelloWall/
    ├── 12345678-1234-5678-1234-567812345678_abc123def456.json
    ├── 87654321-4321-8765-4321-876543218765_xyz789uvw012.json
    └── ...
```

## Usage

### Web Interface

1. Navigate to http://localhost:5000
2. Click the upload area or drag & drop a file
3. Select an IFC or JSON file
4. Click "Upload & Process"
5. View results and component count

### API Usage

```bash
# Upload a file
curl -F "file=@yourfile.ifc" http://localhost:5000/api/upload

# Query entities of a specific type
curl "http://localhost:5000/api/entities?models=HelloWall&entity_types=IfcWallAttributes"

# Get component GUIDs for an entity
curl "http://localhost:5000/api/guids?entity_guids=12345678-1234-5678-1234-567812345678"

# Retrieve component data
curl "http://localhost:5000/api/components?guids=abc123,def456"

# List all loaded models
curl http://localhost:5000/api/models

# Check server status
curl http://localhost:5000/api/status
```

## Configuration

Edit `app.py` to adjust:
- **Port**: Change `port=5000` to desired port
- **Max File Size**: Adjust `MAX_CONTENT_LENGTH`
- **Allowed Extensions**: Modify `ALLOWED_EXTENSIONS`
- **Data Store Path**: Update `FileBasedStore()` initialization

## Troubleshooting

### Server won't start
- Ensure port 5000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Upload fails
- Verify file size is under 500MB
- Check file format (.ifc or .json)
- Ensure `dataStores/fileBased/data/` directory is writable

### No components stored
- Check that JSON files contain an array at root level
- Verify components have `entityGuid` and `guid` fields

## Development

### Debug Mode

The server runs in production mode by default. To enable debug mode, modify `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Logging

Check the terminal output for processing details and any errors.

## Architecture

- **Flask**: Web framework and API server
- **ifcopenshell**: IFC file parsing and processing
- **FileBasedStore**: Component persistence layer

## Future Enhancements

- Additional data store implementations (Database, Cloud Storage)
- Component search and retrieval endpoints
- Batch file processing
- Component filtering and transformation
- Authentication and authorization
