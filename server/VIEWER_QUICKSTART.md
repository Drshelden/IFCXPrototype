# Advanced Viewer - Quick Start

## Getting Started (30 seconds)

1. **Start Server**: `python app.py` (or F5 in VS Code)
2. **Upload Model**: Go to `http://localhost:5000` → Upload IFC file
3. **Open Viewer**: Go to `http://localhost:5000/viewer`
4. **Run Query**: Enter a query and press Enter:
   - Full URL: `http://localhost:5000/api/entities?entity_types=IfcWall`
   - Shorthand: `/api/guids?models=HelloWall`
   - Shorthand: `api/models`

---

## Query Format Options

The viewer accepts queries in multiple formats:

| Format | Example |
|--------|---------|
| **Full URL** | `http://localhost:5000/api/entities?entity_types=IfcWall` |
| **With /api** | `/api/guids?models=HelloWall&entity_types=IfcWallAttributes` |
| **Without /api** | `api/guids?models=HelloWall` |
| **Shorthand** | `guids?models=HelloWall` |

All formats are automatically converted and display component data.

---

## Common Tasks

### Task 1: View All Components in a Model (Full URL Example)
```
Query: http://localhost:5000/api/entities?entity_types=IfcWall
Click: [Execute]
Result: Component data automatically fetched and displayed
View: Tree shows all entities with their components
Select: Check boxes to display in 3D view
```

### Task 2: View All Components (Shorthand)
```
Query: /api/guids?models=HelloWall
Click: [Execute]
View: Tree shows all entities with their components
Select: Check boxes to display in 3D view
```

### Task 3: Find All Walls
```
Query: /api/guids?entity_types=IfcWallAttributes
Click: [Execute]
Result: Shows only wall-type components from all models
Check: Select specific walls to visualize
```

### Task 4: Compare Properties Across Components
```
Query: /api/guids?models=HelloWall&entity_types=IfcWallAttributes,IfcDoorStyle
Click: [Execute]
Expand: Click arrows to see component structure
Check: Multiple components to compare
Scroll: Scroll data table to compare properties side-by-side
```

### Task 5: Inspect Specific Components
```
Query: /api/entity_types?models=HelloWall
Result: Lists all entity types available
Query: /api/guids?entity_types=IfcPropertySet
Select: Check components in tree
View: See all properties in bottom table
```

### Task 6: Work With Multiple Models
```
Query: /api/models
Result: See list of all available models
Query: /api/guids?models=Model1,Model2,Model3
Result: Combines components from multiple models
Compare: Use tree and 3D viewer to analyze across projects
```

---

## Query Cheat Sheet

| Task | Query | Format |
|------|-------|--------|
| Query with full URL | `http://localhost:5000/api/entities?entity_types=IfcWall` | Full URL |
| Get all models | `/api/models` | Shorthand |
| List entity types | `/api/entity_types` | Shorthand |
| All components in a model | `/api/guids?models=HelloWall` | Shorthand |
| Specific component type | `/api/guids?entity_types=IfcPropertySet` | Shorthand |
| Components by entity ID | `/api/guids?entity_guids=12345678-1234-5678-1234-567812345678` | Shorthand |
| Specific components data | `/api/components?guids=abc123,def456` | Shorthand |
| Walls in building | `/api/guids?models=MainBuilding&entity_types=IfcWallAttributes` | Shorthand |
| All property sets | `/api/guids?entity_types=IfcPropertySet` | Shorthand |
| Multiple types | `/api/guids?entity_types=IfcWall,IfcDoor,IfcWindow` | Shorthand |
| Cross-model query | `/api/guids?models=Floor1,Floor2&entity_types=IfcSlab` | Shorthand |

---

## UI Controls Reference

### Query Bar
- **Text Input**: Type REST API query path
- **Execute**: Run the query
- **Clear**: Reset viewer and clear results
- **Status Dot**: Green = ready, animating = busy, red = error

### Left Panel (Tree View)
- **▶ Arrow**: Click to expand/collapse level
- **☑ Checkbox**: 
  - Check parent (entity) → show all components
  - Check child (component) → show that component only
  - Unchecked → hidden from 3D view
- **Count Badge**: Number of items at that level
- **Hierarchy**: Entity → Component → Properties

### Right Panel (3D Viewer)
- **Drag Mouse**: Orbit camera around model
- **Scroll Wheel**: Zoom in/out
- **Grid Toggle**: Show/hide reference grid (checkbox)
- **Axes Toggle**: Show/hide XYZ axes (checkbox)
- **Reset View**: Restore default camera angle
- **Fit All**: Auto-zoom to show all selected objects

### Bottom Panel (Data Table)
- **Column Headers**: GUID | Property | Value
- **Row Count**: Shows total matched properties
- **Hover**: See full value in tooltip
- **Scroll**: Browse through properties
- **Selected**: Shows data for checked components only

---

## Pro Tips

### 💡 Workflow Optimization

1. **Start with discovery**
   - Query `/api/models` first
   - Then `/api/entity_types?models=MyModel`
   - This shows what data is available

2. **Query efficiently**
   - Use model filter to reduce noise
   - Filter by entity type for focused queries
   - Batch related types together

3. **Visualize strategically**
   - Expand tree but don't check everything
   - Start with 3-5 components to understand structure
   - Then add more as needed

4. **Inspect thoughtfully**
   - Expand component tree fully before selecting
   - Look at property names to understand data
   - Use data table for detailed comparison

### ⚡ Performance Tips

- **Large datasets**: Split into multiple smaller queries
- **Slow rendering**: Uncheck grid/axes to reduce load
- **Too many properties**: Collapse component tree to reduce render calls
- **Unresponsive**: Check browser console (F12) for WebGL issues

### 🎯 Debugging

| Issue | Solution |
|-------|----------|
| 3D view is black | Check if Grid/Axes are visible, try Fit All |
| Tree won't expand | Reload page (Ctrl+R) |
| Query fails | Check status bar error message |
| No components showing | Ensure checkboxes are checked in tree |
| Slow performance | Try smaller query (single model, single type) |

---

## Example Workflows

### Workflow A: Explore Building Structure
```
1. Query: /api/models
   → Lists available models

2. Query: /api/entity_types?models=MainBuilding  
   → See what types exist

3. Query: /api/guids?models=MainBuilding&entity_types=IfcWallAttributes
   → Get all walls

4. Check: 2-3 walls in tree
   → View in 3D

5. Inspect: Scroll data table
   → Compare wall properties
```

### Workflow B: Property Investigation
```
1. Query: /api/guids?entity_types=IfcPropertySet
   → Get all property sets

2. Expand: Tree to see structure
   → Understand property hierarchy

3. Check: 5 property sets
   → Load into 3D view

4. Compare: Data table
   → See property name/value patterns
```

### Workflow C: Cross-Model Comparison
```
1. Query: /api/guids?models=Design,Construction,AsBuilt
   → Load same model from 3 phases

2. Check: Same entity in each
   → View 3 versions together

3. Inspect: Differences
   → Track changes in data table
```

---

## Common Queries by Use Case

### Building Analysis
```
/api/guids?models=MainBuilding&entity_types=IfcWallAttributes,IfcSlabAttributes,IfcRoofAttributes
→ View all structural elements
```

### Space Planning
```
/api/guids?entity_types=IfcSpaceAttributes
→ All rooms and spaces
```

### System Design
```
/api/guids?entity_types=IfcPipeSegmentAttributes,IfcElectricalElement
→ MEP components
```

### Material Schedule
```
/api/guids?entity_types=IfcPropertySet
→ All material properties
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Execute query (from input field) |
| **Esc** | (Future) Close menu |
| **Ctrl+L** | Focus query input |
| **F** | (Future) Fit all in 3D |

---

## Getting Help

1. Check **Status Bar** (top right) for error messages
2. Open **Browser Console** (F12 → Console) for details
3. Review **VIEWER_GUIDE.md** for full documentation
4. Check **API_DOCUMENTATION.md** for endpoint details

---

## Next Steps

- [ ] Upload your first IFC file
- [ ] Try 3-4 different queries
- [ ] Explore tree expansion/collapse
- [ ] Toggle component visibility
- [ ] Compare properties in data table
- [ ] Zoom/pan in 3D viewer
- [ ] Try multi-model queries

**Happy exploring! 🚀**
