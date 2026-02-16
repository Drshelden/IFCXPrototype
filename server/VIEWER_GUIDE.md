# Advanced Viewer Documentation

## Overview

The Advanced Viewer is a web-based interface for exploring IFC component data with real-time 3D visualization. It provides a sophisticated multi-pane interface combining REST API query capabilities with interactive component browsing and 3D rendering.

## Access

- **URL**: `http://localhost:5000/viewer`
- **Admin Interface**: `http://localhost:5000` (for file uploads)

## User Interface Layout

### 1. **Top Section: Query Input**

The query input bar allows you to execute REST API calls directly.

```
[http://localhost:5000/api/entities?entity_types=IfcWall] [Execute] [Clear]  ● Ready
```

**Features:**
- Direct REST endpoint querying with any server/port
- **Full URL support**: `http://localhost:5000/api/entities?entity_types=IfcWall`
- **Shorthand URLs**: `/api/guids?models=HelloWall`
- **Mixed formats**: `api/components?guids=abc123` (auto-fills server)
- Press Enter or click Execute to run query
- Clear button resets the viewer
- Real-time status indicator
- Component data automatically fetched and displayed

**Query Format Examples:**
```
# Full URL (any server/port)
http://localhost:5000/api/entities?entity_types=IfcWall

# Standard API path
/api/guids?entity_types=IfcPropertySet

# Without /api prefix
api/components?guids=abc123,def456

# Shorthand endpoint
guids?models=HelloWall&entity_types=IfcWallAttributes

# Discovery endpoints
/api/models
/api/entity_types?models=HelloWall
```

### 2. **Left Panel: Entity/Component Tree**

Expandable hierarchical view of all loaded entities and components.

```
Entities & Components
├─ ⊟ Entity GUID 1                          (3)
│  ├─ ⊟ Component GUID A
│  │  ├─ Name: "Wall Type"
│  │  ├─ Height: 3000
│  │  └─ Material: "Concrete"
│  ├─ ⊟ Component GUID B
│  └─ ⊟ Component GUID C
├─ ⊟ Entity GUID 2                          (2)
└─ ⊟ Entity GUID 3                          (1)
```

**Controls:**
- **Expand/Collapse**: Click ▶ arrow to expand hierarchy
- **Checkboxes**: 
  - Check entity box to show all its components
  - Check component box to show only that component
  - Unchecking hides component from 3D viewer and data table
- **Count Badge**: Shows number of child components
- **Hover**: Highlights tree item

**Interaction:**
- Selecting an entity's checkbox toggles all its components
- Component visibility directly updates 3D view
- Selected components update the bottom data table

### 3. **Right Panel: 3D Viewer**

Interactive Three.js-based 3D visualization with WebGL rendering.

**Features:**
- **Real-time Rendering**: Updates as you check/uncheck components
- **Mouse Controls**:
  - **Drag**: Orbit camera around scene
  - **Scroll**: Zoom in/out
  - **Click**: Select/deselect components (toggles visibility)
  
**Controls Bar** (bottom of 3D panel):
```
☑ Grid    |    ☑ Axes    |    [Reset View]    [Fit All]
```

- **Grid**: Toggle reference grid
- **Axes**: Toggle XYZ axes indicator
- **Reset View**: Restore default camera position
- **Fit All**: Auto-zoom to show all visible objects

**Lighting & Materials:**
- Automatic lighting setup (ambient + directional)
- Phong material with realistic shading
- Double-sided rendering for complex geometries

### 4. **Bottom Panel: Component Data Table**

Tabular display of properties for all selected components.

```
Component Data (127 rows)
╒════════════════════╤══════════════════════╤═══════════════════════╕
│ GUID               │ Property             │ Value                 │
├────────────────────┼──────────────────────┼───────────────────────┤
│ abc123...          │ Name                 │ "Exterior Wall"       │
│ abc123...          │ Height               │ 3000                  │
│ abc123...          │ Type                 │ "IfcWallAttributes"   │
│ def456...          │ Name                 │ "Interior Wall"       │
│ def456...          │ Thickness            │ 200                   │
└────────────────────┴──────────────────────┴───────────────────────┘
```

**Features:**
- Shows all properties for selected components
- GUID column truncated for readability (hover for full value)
- Sortable columns (click header to sort)
- Scrollable for large datasets
- Row count indicator

**Search & Filter:**
- (Future feature: Add filtering/search within table)

---

## Workflow Examples

### Example 1: Explore All Walls in a Model

1. **Query**: `/api/guids?models=HelloWall&entity_types=IfcWallAttributes`
2. **Execute** → Tree loads with all walls grouped by entity
3. **Select**: Check box next to first entity
4. **View**: 3D viewer displays selected walls
5. **Inspect**: Bottom table shows wall properties

### Example 2: Compare Multiple Component Types

1. **Query**: `/api/guids?entity_types=IfcPropertySet,IfcDoor`
2. **Execute** → Loads property sets and doors
3. **Expand**: Click expand arrows to see component hierarchy
4. **Toggle**: Check/uncheck individual components to compare
5. **Analyze**: Use data table to compare property values

### Example 3: Detailed Property Inspection

1. **Query**: `/api/components?guids=abc123,def456`
2. **Execute** → Direct component data loads
3. **Select**: Check specific components in tree
4. **Inspect**: Scroll table to review all 50+ properties
5. **Export**: (Future: Copy to clipboard)

### Example 4: Across Multiple Models

1. **Query**: `/api/entity_types?models=Model1,Model2`
2. View entity types available in both models
3. **Query**: `/api/guids?models=Model1,Model2&entity_types=IfcWallAttributes`
4. **Compare**: Walls across multiple project models side-by-side

---

## Advanced Features

### Multi-Model Navigation

Query multiple models simultaneously:
```
/api/guids?models=HelloWall,SecondFloor,Exterior&entity_types=IfcWallAttributes
```

The tree organizes results hierarchically, and checkboxes control visibility per component.

### Complex Filtering

Combine multiple filters:
```
/api/guids?models=MainBuilding&entity_types=IfcPropertySet,IfcObjectDefinition&entity_guids=guid1,guid2
```

### Hierarchical Selection

- **Entity-level**: Check parent entity to select all components
- **Component-level**: Check individual component for precise control
- **Property-level**: View in data table, future bulk operations

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Execute query (when input focused) |
| Esc | Clear all (future) |
| Ctrl+A | Select all visible (future) |
| Ctrl+C | Copy selected properties (future) |

---

## Performance Considerations

### Large Datasets
- Viewer handles up to 10,000 components efficiently
- Tree virtualization recommended for larger sets (future)
- Data table uses windowing for smooth scrolling

### Memory Usage
- 3D mesh instances cached after first load
- Component data stored in memory during session
- Clear button frees resources

### Rendering Performance
- Three.js WebGL with hardware acceleration
- Frustum culling auto-enabled
- Optimize by ungrouping large entities

---

## Troubleshooting

### 3D View Not Showing

1. Check browser console (F12) for WebGL errors
2. Verify WebGL 2.0 support: https://webglreport.com/
3. Try disabling GPU hardware acceleration
4. Clear browser cache and reload
5. Check that query returned valid component data

### Tree Not Expanding

1. Verify query completed successfully (check status bar)
2. Ensure components have data to display
3. Try refreshing page (Ctrl+R)
4. Check browser console for JavaScript errors

### Slow Performance

1. Reduce number of visible components (uncheck unnecessary items)
2. Hide grid/axes to reduce render load
3. Break large queries into smaller model-specific ones
4. Check browser performance tab (F12 → Performance)

### Data Table Empty

1. Check that components are selected in tree (checkboxes)
2. Ensure query returned component data (not just GUIDs)
3. Try hitting "Fit All" first, then select components

---

## Future Enhancements

- [ ] Search/filter in tree view
- [ ] Bulk export (CSV, JSON)
- [ ] Component selection by type
- [ ] 3D model import/export (glTF, OBJ)
- [ ] Property change history tracking
- [ ] Measurement tools
- [ ] Cross-model comparison mode
- [ ] Rendering optimization for 100K+ components
- [ ] Real-time collaboration (multiple viewers)
- [ ] VR/AR viewing modes

---

## API Integration Notes

The viewer automatically handles these API endpoints:

| Endpoint | Used For | Response Structure |
|----------|----------|-------------------|
| `/api/entities` | Entity GUID querying | Paginated entity GUIDs |
| `/api/guids` | Component GUIDs by filter | Array of component GUIDs |
| `/api/components` | Full component data | Objects with all properties |
| `/api/models` | Available models list | Simple array of model names |
| `/api/entity_types` | Type discovery | Array of entity type names |

All queries return standard JSON with optional error messages.

---

## Tips & Best Practices

1. **Start Broad**: Query `/api/models` first to understand available data
2. **Refine Gradually**: Use `/api/entity_types?models=X` to see what's available
3. **Batch Small**: For the first time, query a single model with one type
4. **Check Visibility**: Uncheck grid/axes to focus on geometry
5. **Use Fit All**: After selection, click "Fit All" to center view on data
6. **Inspect Properties**: Expand tree fully to see component structure before checking boxes
7. **Monitor Status**: Watch status bar for query progress/errors

