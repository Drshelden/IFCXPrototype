# Viewer Architecture & Implementation Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VIEWER (viewer.html)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐    │
│  │  Query Input │  │ Tree View   │  │ 3D Viewer      │    │
│  │  (REST API)  │  │ (Navigation)│  │ (Three.js)     │    │
│  │              │  │             │  │                │    │
│  │ /api/guids   │  │ Entities    │  │ WebGL Canvas   │    │
│  │ /api/models  │  │ Components  │  │ Interactive    │    │
│  │ /api/entity_ │  │ Properties  │  │ Visualization  │    │
│  │  types       │  │             │  │                │    │
│  └──────────────┘  └─────────────┘  │ Lighting       │    │
│                                      │ Materials      │    │
│  ┌──────────────────────────────────┤                │    │
│  │ Data Table (Properties Display)   │ Mouse Control  │    │
│  │ Shows selected component values   └────────────────┘    │
│  └──────────────────────────────────────────────────────────┘
│                         ↓
├─────────────────────────────────────────────────────────────┤
│                 REST API (Flask - app.py)                    │
├─────────────────────────────────────────────────────────────┤
│  /api/models       → Returns available models              │
│  /api/entity_types → Returns entity type list              │
│  /api/entities     → Returns entity GUIDs (with filters)   │
│  /api/guids        → Returns component GUIDs (with filters)│
│  /api/components   → Returns full component data           │
└─────────────────────────────────────────────────────────────┘
                         ↓
├─────────────────────────────────────────────────────────────┤
│           Memory Tree (memoryTree.py)                        │
├─────────────────────────────────────────────────────────────┤
│  Models {                                                    │
│    "ModelName": {                                           │
│      "by_entity": { entityGuid: [componentGuids] },        │
│      "by_type": { typeName: [componentGuids] },            │
│      "by_guid": { componentGuid: {full_data} }             │
│    }                                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
├─────────────────────────────────────────────────────────────┤
│       File-Based Store (dataStores/fileBased/)              │
├─────────────────────────────────────────────────────────────┤
│  /data/ModelName/                                           │
│    ├── entityGuid_guid.json                                │
│    ├── entityGuid_guid.json                                │
│    └── ...                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Query Execution Flow

```
User enters query
    ↓
JavaScript: fetch() to REST endpoint
    ↓
Flask app.py: Route handler
    ↓
Memory Tree: Query against indices
    ↓
JSON Response
    ↓
JavaScript: Parse response
    ↓
Build tree structure
    ↓
Update 3D viewer
    ↓
Populate data table
```

### 2. Component Selection Flow

```
User checks component checkbox
    ↓
JavaScript: Add GUID to selectedGuids Set
    ↓
Update mesh visibility in Three.js scene
    ↓
Query component data from currentData
    ↓
Build table rows
    ↓
Render table with selected properties
    ↓
Update row count display
```

## Technical Components

### Frontend Components

#### 1. **Query Input System**
- **File**: `viewer.html` (lines 869-950)
- **Function**: `executeQuery()`
- **Handles**:
  - Full URL support (with any server/port)
  - Shorthand path parsing (e.g., `/api/guids`, `api/guids`, `guids`)
  - Intelligent response type detection
  - Automatic component data fetching
  - Error handling with user-friendly messages
  - Status display
  
**URL Format Support:**
```
User Input → Normalized URL → API Fetch → Response Processing

Full URL:     http://localhost:5000/api/entities?entity_types=IfcWall
              → Used as-is
              
Path URL:     /api/entities?entity_types=IfcWall
              → Prepended with http://localhost:5000
              
Shorthand:    entities?entity_types=IfcWall
              → Converted to http://localhost:5000/api/entities?...
              
Mixed:        api/guids?models=HelloWall
              → Converted to http://localhost:5000/api/guids?...
```

**Response Processing:**
- Detects endpoint type by response structure
- `/api/entities` → Fetches entity GUIDs, then retrieves component data
- `/api/guids` → Fetches component GUIDs, then retrieves component data
- `/api/components` → Uses component data directly
- `/api/models` → Displays models list
- `/api/entity_types` → Displays entity types list

```javascript
async function executeQuery() {
    // Parse query text - supports full URLs with any server
    let url = input;
    if (url.startsWith('http://') || url.startsWith('https://')) {
        // Full URL - use as-is
    } else if (url.startsWith('/')) {
        url = 'http://localhost:5000' + url;
    } else if (url.startsWith('api/')) {
        url = 'http://localhost:5000/' + url;
    } else {
        url = 'http://localhost:5000/api/' + url;
    }
    
    // Fetch data from any server
    const response = await fetch(url);
    const apiData = await response.json();
    
    // Intelligently process response
    if (apiData.entity_guids) {
        // Get component data for entities
        fetchComponentsForEntities();
    } else if (apiData.component_guids) {
        // Get component data for GUIDs
        fetchComponentData();
    }
    
    // Update all panels
    updateUI(data);
}
```

#### 2. **Tree View System**
- **File**: `viewer.html` (lines 600-750)
- **Functions**: `buildTree()`, `createTreeItem()`, `createPropertyItem()`
- **Structure**:
  - Recursive tree generation from data
  - Expandable/collapsible items
  - Checkboxes for visibility control
  - Count badges for item quantification

```javascript
function buildTree(data) {
    // For each entity
    Object.keys(data.entities).forEach(entityGuid => {
        // Create entity item
        const entityItem = createTreeItem(entityGuid, 'entity', count);
        
        // For each component under entity
        data.entities[entityGuid].forEach(componentGuid => {
            // Create component item
            const componentItem = createTreeItem(componentGuid, 'component');
            
            // For each property
            Object.keys(componentData).forEach(prop => {
                // Add property item
            });
        });
    });
}
```

#### 3. **3D Viewer (Three.js)**
- **File**: `viewer.html` (lines 800-1200)
- **Functions**: `init3DViewer()`, `addMeshToScene()`, `setupMouseControls()`
- **Features**:
  - Scene setup with lighting
  - Camera orbit controls
  - Mesh visibility toggling
  - Grid/Axes overlays
  - Zoom/pan/rotate via mouse

```javascript
function init3DViewer() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(...);
    renderer = new THREE.WebGLRenderer({canvas});
    
    // Lighting
    addAmbientLight(); // Diffuse
    addDirectionalLight(); // Shadows
    
    // Mouse controls
    setupMouseControls(); // Orbit pattern
    
    // Animation loop
    animate(); // Render every frame
}
```

#### 4. **Data Table System**
- **File**: `viewer.html` (lines 1300-1400)
- **Function**: `updateTable()`, `updateTableForSelection()`
- **Rendering**:
  - Dynamic HTML table from row data
  - Truncated values with tooltips
  - Row counting
  - Scrollable container

```javascript
function updateTable(rows) {
    let html = '<table><thead>...';
    rows.forEach(row => {
        html += `<tr>
            <td>${row.guid}</td>
            <td>${row.key}</td>
            <td>${row.value}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}
```

### Backend Components

#### 1. **Flask Routes** (app.py)
- **Route** `/viewer` → `viewer()` function
- **Template** → `templates/viewer.html`
- Serves the complete viewer single-page application

#### 2. **Query Endpoints** (app.py)

| Endpoint | Handler | Returns |
|----------|---------|---------|
| `/api/models` | `models()` | List of model names |
| `/api/entity_types` | `entity_types()` | Filtered entity type list |
| `/api/entities` | `entities()` | Entity GUIDs with filters |
| `/api/guids` | `guids()` | Component GUIDs with filters |
| `/api/components` | `components()` | Full component data |

#### 3. **Memory Tree** (memoryTree.py)
- **Structure**:
  ```python
  {
      "ModelName": {
          "by_entity": {},    # entityGuid → [componentGuids]
          "by_type": {},      # typeName → [componentGuids]
          "by_guid": {}       # componentGuid → {data}
      }
  }
  ```
- **Key Methods**:
  - `refresh_from_store()` - Load from disk
  - `get_entity_guids()` - Query with filters
  - `get_component_guids()` - Query with filters
  - `get_components()` - Retrieve data

## Data Structures

### Query Response Format (Example)

```json
{
  "component_guids": [
    "abc123def456...",
    "ghi789jkl012...",
    "mno345pqr678..."
  ],
  "count": 3
}
```

### Component Data Format (Example)

```json
{
  "guid": "abc123def456...",
  "entityGuid": "ent123...",
  "type": "IfcWallAttributes",
  "Name": "Exterior Wall",
  "Height": 3000,
  "Thickness": 200,
  "Material": "Concrete",
  "description": "South facade wall",
  "properties": {
    "FireRating": "2H",
    "SoundTransmission": 45
  }
}
```

### Tree Data Structure (Internal)

```javascript
{
  entities: {
    "entity-guid-1": ["component-guid-1", "component-guid-2"],
    "entity-guid-2": ["component-guid-3"]
  },
  components: {
    "component-guid-1": { guid, type, Name, Height, ... },
    "component-guid-2": { guid, type, Name, Width, ... },
    "component-guid-3": { guid, type, Name, ... }
  }
}
```

## Interaction Patterns

### Pattern 1: Query → Parse → Display

```
Input: /api/guids?models=HelloWall
        ↓
Parse: Identify query type (guids with models filter)
        ↓
API: Fetch component GUIDs
        ↓
Transform: Get component data for each GUID
        ↓
Display: Build tree with entities containing components
        ↓
User interacts: Check boxes in tree
```

### Pattern 2: Selection → Visibility → View

```
User checks checkbox for component
        ↓
selectedGuids.add(componentGuid)
        ↓
objects3d.get(guid).visible = true
        ↓
Next animation frame renders visible meshes
        ↓
Data table updates with component properties
```

### Pattern 3: Mouse Input → Camera → Rendering

```
User drags mouse over canvas
        ↓
Calculate delta movement
        ↓
Update camera spherical coordinates
        ↓
Camera lookAt(0, 0, 0)
        ↓
requestAnimationFrame triggers render()
        ↓
Three.js performs render(scene, camera)
```

## Performance Optimizations

### 1. **Memory Management**
- Components cached after first fetch
- Mesh instances reused, only visibility toggled
- Garbage collection on "Clear"

### 2. **Rendering Optimization**
- Three.js frustum culling automatic
- Double-precision math for accuracy
- Hardware acceleration via WebGL 2.0

### 3. **Query Efficiency**
- Set-based filtering in memory tree (O(1) lookups)
- Comma-separated parameters parsed once
- Batch API calls when possible

### 4. **DOM Updates**
- Minimal re-renders via innerHTML replacement
- Table uses HTML scrolling, not JavaScript pagination
- Tree items don't re-render during collapse

## Future Enhancement Opportunities

### Short-term
- [ ] Search/filter in tree view
- [ ] Export selected components (CSV, JSON)
- [ ] Keyboard shortcuts
- [ ] Tree item count optimization

### Medium-term
- [ ] Real-time shape representation rendering
- [ ] Component selection by drag-box in 3D
- [ ] Property-based filtering overlay
- [ ] Color-coding by type/entity

### Long-term
- [ ] Streaming for large datasets
- [ ] WebWorker for query parsing
- [ ] Advanced shaders/materials
- [ ] VR/AR viewer modes
- [ ] Collaborative viewing (multi-user)

## Testing Checklist

### Functionality Tests
- [ ] Query execution with various parameters
- [ ] Tree expansion/collapse all levels
- [ ] Checkbox toggling updates visibility
- [ ] 3D view renders selected components
- [ ] Data table shows correct properties
- [ ] Zoom/pan/rotate works smoothly

### Edge Cases
- [ ] Empty query results
- [ ] Very large component sets (1000+)
- [ ] Special characters in property names
- [ ] Browser without WebGL support
- [ ] Mobile responsiveness

### Performance Tests
- [ ] Load time for 100 components
- [ ] Rendering with 500 visible objects
- [ ] Memory usage over extended session
- [ ] Mouse responsiveness during high render load

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome 90+ | ✅ Full | Best performance |
| Firefox 88+ | ✅ Full | Slightly slower rendering |
| Safari 14+ | ✅ Full | Good performance |
| Edge 90+ | ✅ Full | Chromium-based |
| IE 11 | ❌ None | No WebGL 2.0 support |

## Troubleshooting Guide

### 3D Viewer Not Working
```
Checklist:
1. Check browser WebGL support: webglreport.com
2. Enable hardware acceleration in browser
3. Check console (F12) for errors
4. Try different browser
5. Verify graphics driver is updated
```

### Query Failures
```
Checklist:
1. Verify Flask server is running
2. Check query syntax in status bar
3. Look for 404/500 errors
4. Ensure file was uploaded to server
5. Try simpler query (e.g., /api/models)
```

### Performance Issues
```
Solutions:
1. Reduce visible components (uncheck non-essential)
2. Hide grid/axes to reduce geometry
3. Query smaller datasets first
4. Check browser memory usage (DevTools)
5. Clear cache and reload
```

