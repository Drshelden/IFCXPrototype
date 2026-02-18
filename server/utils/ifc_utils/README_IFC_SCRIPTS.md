# IFC Schema Utilities Documentation

This directory contains Python scripts for querying, analyzing, and generating IFC (Industry Foundation Classes) schema information from IFCOpenShell.

## Prerequisites

- Python 3.9+
- IFCOpenShell 0.8.4+ installed in the virtual environment
- Virtual environment: `.venv/Scripts/python.exe`

## Scripts

### 1. generate_ifc_hierarchy.py

**Purpose**: Generates a complete IFC4 class hierarchy with parent-child relationships in a nested JSON structure. Can also output as an indented text file for visual browsing.

**Usage**:
```bash
# Generate JSON hierarchy
python generate_ifc_hierarchy.py

# Generate text tree with tabs for visual hierarchy
python generate_ifc_hierarchy.py --text-tree
```

**Output Files**: 
- `IFC_Classes.json` (default JSON output)
- `IFC_Classes_Tree.txt` (when using --text-tree)

**Output Format**:
```json
{
  "metadata": {
    "generated_by": "generate_ifc_hierarchy.py",
    "ifcopenshell_version": "0.8.4.post1",
    "schema": "IFC4",
    "statistics": {
      "total_classes": 776,
      "root_classes": 59,
      "max_depth": 9
    }
  },
  "classes": [
    {
      "name": "IfcRoot",
      "children": [
        {
          "name": "IfcObjectDefinition",
          "children": [...]
        }
      ]
    }
  ]
}
```

**Text Tree Format** (when using `--text-tree`):
```
IfcRoot
	IfcObjectDefinition
		IfcContext
			IfcProject
			IfcProjectLibrary
		IfcObject
			IfcActor
			IfcControl
				IfcActionRequest
				IfcApprovalRelationship
				...
			IfcGroup
```

**Key Features**:
- All 776 IFC entities extracted from IFC4 schema
- Hierarchical nesting showing inheritance relationships
- 59 root classes with maximum depth of 9 levels
- No attributes included in this version (focus on structure)

---

### 2. generate_ifc_flat.py

**Purpose**: Generates an alphabetically sorted flat list of all IFC classes with their attributes and parent relationships.

**Usage**:
```bash
python generate_ifc_flat.py
```

**Output File**: `IFC_Classes_Flat.json`

**Output Format**:
```json
{
  "metadata": {
    "generated_by": "generate_ifc_flat.py",
    "ifcopenshell_version": "0.8.4.post1",
    "schema": "IFC4",
    "statistics": {
      "total_classes": 776,
      "root_classes": 59,
      "total_attributes": 5264,
      "max_attributes_class": "IfcTaskTimeRecurring",
      "max_attributes_count": 21
    }
  },
  "classes": [
    {
      "name": "IfcActionRequest",
      "parent": "IfcControl",
      "attributes": ["PredefinedType", "Status", "LongDescription"]
    },
    {
      "name": "IfcActor",
      "parent": "IfcObject",
      "attributes": ["TheActor"]
    }
  ]
}
```

**Key Features**:
- Alphabetically sorted list of all 776 classes
- Includes parent class information for easy reference
- Lists all attributes for each class
- Flat structure (no nesting) for easier searching
- Statistics show class with most attributes (21 for IfcTaskTimeRecurring)

---

### 3. ifc_hierarchy_query.py

**Purpose**: Interactive and command-line tool for querying IFC class hierarchy relationships.

**Usage - Command Line**:
```bash
# Check if IfcWall is a subclass of IfcElement
python ifc_hierarchy_query.py issubclass IfcWall IfcElement

# Returns exit code 0 if true, 1 if false
```

**Usage - Interactive Mode**:
```bash
python ifc_hierarchy_query.py
# Then enter commands:
# > issubclass IfcWall IfcElement
# > parent IfcWall
# > parents IfcWall
# > children IfcElement
# > subclasses IfcElement
# > path IfcWall
# > help
# > quit
```

**Interactive Commands**:
- `issubclass <class> <base>` - Check if class inherits from base
- `parent <class>` - Get direct parent
- `parents <class>` - Get all parent classes up the hierarchy
- `children <class>` - Get direct children
- `subclasses <class>` - Get all descendants recursively
- `path <class>` - Get full path from root to class
- `help` - Show command help
- `quit` - Exit interactive mode

**Output**: Console output only (no file)

**Example Output**:
```
IfcWall is a subclass of IfcElement

All parents of IfcWall:
  - IfcBuildingElement
  - IfcElement
  - IfcProduct
  - IfcObject
  - IfcObjectDefinition
  - IfcRoot
```

---

### 4. ifc_descendants_export.py

**Purpose**: Given a base class, exports all descendants (including the base class) as a JSON array.

**Usage**:
```bash
# Pretty-printed output
python ifc_descendants_export.py IfcWall --pretty

# Compact output
python ifc_descendants_export.py IfcElement

# With Component suffix appended
python ifc_descendants_export.py IfcWall --component --pretty
```

**Output**: Console only (JSON array)

**Output Examples**:

Basic output:
```json
[
  "IfcWall",
  "IfcWallElementedCase",
  "IfcWallStandardCase"
]
```

With `--component` flag:
```json
[
  "IfcWallComponent",
  "IfcWallElementedCaseComponent",
  "IfcWallStandardCaseComponent"
]
```

**Options**:
- `--pretty` - Pretty-print the JSON array
- `--component` - Append "Component" suffix to each class name

**Key Features**:
- Returns just the class array (no wrapper metadata)
- Alphabetically sorted
- Component suffix useful for generating component class names

---

### 5. ifc_schema_generator.py

**Purpose**: Generates detailed JSON schemas from root classes, including all descendants with full attribute type information and constraints.

**Usage**:
```bash
# Display to console
python ifc_schema_generator.py IfcWall --pretty

# Save to file
python ifc_schema_generator.py IfcElement --output schema.json --pretty

# Multiple root classes
python ifc_schema_generator.py IfcElement IfcProduct --output schema_combined.json --pretty
```

**Output File**: User-specified (e.g., `schema.json`)

**Output Format**:
```json
{
  "root_classes": ["IfcWall"],
  "total_classes": 3,
  "classes": [
    {
      "name": "IfcWall",
      "parent": "IfcBuildingElement",
      "attributes": [
        {
          "name": "GlobalId",
          "type": "<type IfcGloballyUniqueId: <string>>",
          "optional": false,
          "derived": false
        },
        {
          "name": "OwnerHistory",
          "type": "<entity IfcOwnerHistory>",
          "optional": true,
          "derived": false
        },
        {
          "name": "PredefinedType",
          "type": "<enumeration IfcWallTypeEnum: (MOVABLE, PARAPET, PARTITIONING, PLUMBINGWALL, SHEAR, SOLIDWALL, STANDARD, POLYGONAL, ELEMENTEDWALL, USERDEFINED, NOTDEFINED)>",
          "optional": true,
          "derived": false
        }
      ]
    }
  ]
}
```

**Attribute Information Provided**:
- **name**: Attribute name
- **type**: Full type specification including:
  - Named types: `<type IfcGloballyUniqueId: <string>>`
  - Entity references: `<entity IfcOwnerHistory>>`
  - Enumerations with all valid values
  - Aggregates: `<list of ...>`
- **optional**: Whether attribute is required (false) or optional (true)
- **derived**: Whether attribute is computed (true) or stored (false)

**Options**:
- `--pretty` - Pretty-print the JSON output
- `--output FILE` - Save to file instead of console

**Key Features**:
- Supports multiple root classes
- Includes all descendants
- Complete type information and constraints
- Derived status tracking
- Perfect for code generation and validation

---

## Output Files Reference

### Automatically Generated Files

#### `IFC_Classes.json`
- **Generated By**: `generate_ifc_hierarchy.py` (default)
- **Size**: ~100KB
- **Format**: Nested JSON structure
- **Contents**: 
  - Metadata (version, schema info, statistics)
  - 776 IFC entities arranged in parent-child hierarchy
  - 59 root classes with maximum depth of 9 levels
- **Use Cases**: 
  - Traversing IFC hierarchy programmatically
  - UI tree widgets
  - Understanding class relationships
- **Sample Root Classes**: IfcRoot, IfcActorRole, IfcAddress, IfcAppliedValue, IfcSimplePropertyTemplate, etc.

#### `IFC_Classes_Tree.txt`
- **Generated By**: `generate_ifc_hierarchy.py --text-tree`
- **Size**: ~30KB
- **Format**: Plain text with tab indentation
- **Contents**: 
  - 776 IFC entities arranged hierarchically
  - Tab characters denote nesting level (1 tab = child, 2 tabs = grandchild, etc.)
  - One class per line
  - Maximum depth: 9 levels
- **Use Cases**:
  - Visual inspection of hierarchy in text editor
  - Grep/search operations on hierarchy
  - Documentation and reference
- **Sample**:
  ```
  IfcRoot
  	IfcObjectDefinition
  		IfcContext
  			IfcProject
  ```

#### `IFC_Classes_Flat.json`
- **Generated By**: `generate_ifc_flat.py`
- **Size**: ~50KB
- **Format**: JSON array with metadata
- **Contents**:
  - 776 IFC entities alphabetically sorted
  - For each class: name, parent, and all attributes
  - Statistics: 5,264 total attributes across all classes
  - Max attributes: 21 (IfcTaskTimeRecurring)
- **Use Cases**:
  - Searching for specific classes
  - Reference lookups
  - Attribute enumeration
  - Database schema generation
- **Statistics**:
  - Average attributes per class: 6.8
  - Classes with no attributes: ~50
  - Classes with 15+ attributes: ~15

#### `schema_wall_detailed.json`
- **Generated By**: `ifc_schema_generator.py IfcWall --pretty`
- **Size**: ~40KB
- **Format**: JSON with detailed attribute metadata
- **Contents**:
  - Root class: IfcWall
  - Descendants: IfcWallElementedCase, IfcWallStandardCase
  - For each attribute: name, type, optional flag, derived flag
  - Complete enumeration values for type attributes
- **Use Cases**:
  - Wall modeling
  - Understanding IfcWall API
  - Code generation for wall handling

#### `schema_elements.json`
- **Generated By**: `ifc_schema_generator.py IfcElement IfcProduct --pretty`
- **Size**: ~500KB
- **Format**: JSON with detailed attribute metadata
- **Contents**:
  - Root classes: IfcElement, IfcProduct
  - Total classes: 310+ descendants
  - Complete type information for all attributes
  - Constraint metadata (optional, derived status)
- **Use Cases**:
  - Comprehensive schema for building element handling
  - Analysis of product/element relationships
  - Code generation for element-based systems

---

## Generated Files Summary

| File | Script | Size | Classes | Purpose |
|------|--------|------|---------|---------|
| `IFC_Classes.json` | generate_ifc_hierarchy.py | ~100KB | 776 | Nested hierarchy for traversal |
| `IFC_Classes_Tree.txt` | generate_ifc_hierarchy.py --text-tree | ~30KB | 776 | Visual text-based hierarchy |
| `IFC_Classes_Flat.json` | generate_ifc_flat.py | ~50KB | 776 | Alphabetical searchable list |
| `schema_wall_detailed.json` | ifc_schema_generator.py | ~40KB | 3 | Wall hierarchy with full schema |
| `schema_elements.json` | ifc_schema_generator.py | ~500KB | 310+ | Element/Product schema |

---

## Common Use Cases

### 1. Check if a class is a subclass of another
```bash
python ifc_hierarchy_query.py issubclass IfcWall IfcElement
```

### 2. Get all elements in a hierarchy
```bash
python ifc_descendants_export.py IfcElement --pretty
```

### 3. Generate schema for code generation
```bash
python ifc_schema_generator.py IfcElement IfcProduct --output app_schema.json --pretty
```

### 4. Get all descendants with "Component" suffix
```bash
python ifc_descendants_export.py IfcElement --component > components.json
```

### 5. Query class information interactively
```bash
python ifc_hierarchy_query.py
> path IfcWall
> subclasses IfcElement
```

---

## Quick Reference Table

### Finding Classes

**Need to...** | **Command**
---|---
Check if X is subclass of Y | `python ifc_hierarchy_query.py issubclass X Y`
Find all classes under X | `python ifc_descendants_export.py X --pretty`
Find parent of X | `python ifc_hierarchy_query.py parent X`
Get full hierarchy path of X | `python ifc_hierarchy_query.py path X`
View full hierarchical tree | `cat IFC_Classes_Tree.txt` or `less IFC_Classes_Tree.txt`
Search for class attributes | `grep -i "attributeName" IFC_Classes_Flat.json`
Find classes with most attributes | `grep "max_attributes" IFC_Classes_Flat.json`

### Generating Schemas

**Need to...** | **Command**
---|---
Generate Wall schema | `python ifc_schema_generator.py IfcWall --output schema_wall.json --pretty`
Generate Element + Product schema | `python ifc_schema_generator.py IfcElement IfcProduct --output full.json --pretty`
Export as JSON array only | `python ifc_descendants_export.py IfcWall --pretty`
Export with Component suffix | `python ifc_descendants_export.py IfcWall --component --pretty`
Generate complete hierarchy | `python generate_ifc_hierarchy.py`
Generate text-based hierarchy | `python generate_ifc_hierarchy.py --text-tree`
Generate flat searchable list | `python generate_ifc_flat.py`

---

## Advanced Examples

### Example 1: Find all Building Elements and export as components
```bash
python ifc_descendants_export.py IfcBuildingElement --component --pretty > building_components.json
# Output:
# [
#   "IfcBuildingElementComponent",
#   "IfcBeamComponent",
#   "IfcColumnComponent",
#   "IfcCoveringComponent",
#   ...
# ]
```

### Example 2: Query multiple hierarchy paths
```bash
python ifc_hierarchy_query.py
> path IfcWall
IfcWall is at path: IfcRoot -> IfcObjectDefinition -> IfcObject -> IfcProduct -> IfcElement -> IfcBuildingElement -> IfcWall

> path IfcBeam
IfcBeam is at path: IfcRoot -> IfcObjectDefinition -> IfcObject -> IfcProduct -> IfcElement -> IfcBuildingElement -> IfcBeam

> quit
```

### Example 3: Generate schemas for documentation
```bash
# Generate comprehensive schema for construction elements
python ifc_schema_generator.py IfcBuildingElement --output schema_building.json --pretty

# Generate for material properties
python ifc_schema_generator.py IfcMaterial IfcMaterialProperties --output schema_materials.json --pretty
```

### Example 4: Get all geometric types
```bash
python ifc_descendants_export.py IfcGeometricRepresentationItem > geometric_types.json
# Shows all geometric shapes: Line, Polyline, CircularArc, CurveStyleFontAndScaling, etc.
```

### Example 5: Analyze hierarchy depth
```bash
# Check the longest paths in the hierarchy
python ifc_hierarchy_query.py
> path IfcWallStandardCase  # Depth 9 (deepest common case)
> path IfcExtrudedAreaSolid  # Different branch
> path IfcPropertySingleValue  # Shallow branch
> quit
```

---

## Attribute Type Guide

When reviewing attribute types in schema output, you'll see several type formats:

### Basic Types
- `<type IfcGloballyUniqueId: <string>>` - String-based unique identifier
- `<type IfcLabel: <string>>` - Display label text
- `<type IfcLength: <number>>` - Measurement in project units
- `<type IfcPositiveLength: <number>>` - Non-negative measurement
- `<type IfcPositiveRatioMeasure: <number>>` - Ratio between 0 and 1

### Entity References
- `<entity IfcOwnerHistory>` - Links to ownership/history information
- `<entity IfcObjectPlacement>` - Placement/location coordinates
- `<entity IfcProductDefinitionShape>` - Geometric representation

### Aggregates
- `<list of <entity IfcRelAssigns>>` - List of relationships
- `<set of <entity IfcOrientedEdge>>` - Set (unique items) of edges
- `<array of <type IfcLength> [0:?]>` - Variable-length array of measurements

### Enumerations
- `<enumeration IfcWallTypeEnum: (MOVABLE, PARAPET, PARTITIONING, PLUMBINGWALL, SHEAR, SOLIDWALL, STANDARD, ...)>`
  - Lists all valid values in parentheses
  - Class-specific allowed values

### Optional vs. Required
- `"optional": false` - Attribute MUST be provided
- `"optional": true` - Attribute MAY be omitted
- `"derived": true` - Attribute is computed (not stored directly)
- `"derived": false` - Attribute is explicitly stored

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ifcopenshell'"

**Solution**:
```bash
# Activate virtual environment first
.venv\Scripts\Activate.ps1  # PowerShell
.venv\Scripts\activate.bat   # CMD

# Verify installation
python -c "import ifcopenshell; print(ifcopenshell.version)"

# Should output: 0.8.4.post1 (or similar)
```

### Issue: Script runs but produces empty output

**Solution**:
```bash
# Check if IFCOpenShell can access the schema
python -c "from ifcopenshell_wrapper import schema_by_name; s = schema_by_name('IFC4'); print(len(list(s.entities())))"

# Should output: 776

# If not, reinstall ifcopenshell:
pip install --upgrade ifcopenshell==0.8.4.post1
```

### Issue: JSON output is malformed

**Solution**:
```bash
# Validate JSON output
python -c "import json; json.load(open('IFC_Classes.json'))"

# If error, check the file for incomplete writes or encoding issues
# Regenerate the file:
python generate_ifc_hierarchy.py
```

### Issue: Script is slow (>10 seconds)

**Reason**: First run loads entire schema + 776 entities

**Solution**: 
- First run is slower (2-5 seconds normal)
- If >10 seconds, system may be under heavy load
- Consider running during off-peak times
- Results are cached in JSON files after first generation

### Issue: "Exit code 1"

**Troubleshooting**:
```bash
# Run with explicit error output
python script_name.py 2>&1 | Out-String

# Check for specific error messages
python script_name.py --help

# Verify syntax
python -m py_compile generate_ifc_hierarchy.py
```

---

## Performance Notes

- **Schema Loading**: ~2-5 seconds first run (776 entities loaded)
- **Hierarchy Generation**: 1-2 seconds additional
- **Flat List Generation**: <1 second
- **Query Operations**: <100ms per query
- **Schema Detail Generation**: 2-5 seconds depending on descendants

**Optimization Tips**:
1. Run query tool in interactive mode to amortize startup cost
2. Cache generated JSON files; regenerate only when schema changes
3. For batch operations, import scripts as modules rather than subprocess calls
4. Use `--output FILE` to write to disk; pipes are slower

---

## Schema Statistics

### Overall
- **Total Classes**: 776
- **Root Classes**: 59
- **Maximum Depth**: 9 levels
- **Total Attributes**: 5,264
- **Average Attributes per Class**: 6.8

### Class Distribution by Depth
- **Depth 0** (Root): 59 classes
- **Depth 1**: ~150 classes
- **Depth 2-3**: ~350 classes
- **Depth 4-5**: ~150 classes
- **Depth 6-9**: ~67 classes (less common cases)

### Largest Classes by Attribute Count
1. **IfcTaskTimeRecurring**: 21 attributes
2. **IfcTask**: 20 attributes
3. **IfcWorkSchedule**: 18 attributes
4. **IfcProjectLibrary**: 17 attributes
5. Multiple classes with 15 attributes

### Common Base Classes
- **IfcRoot**: Base for 776 entities (all classes)
- **IfcObjectDefinition**: ~300 descendants (primary object types)
- **IfcProduct**: ~180 descendants (physical/spatial objects)
- **IfcElement**: ~137 descendants (specific building elements)
- **IfcBuildingElement**: ~45 descendants (walls, columns, beams, etc.)

---

## Implementation Details

### Schema Access
- **Source**: IFCOpenShell 0.8.4.post1 `ifcopenshell_wrapper` module
- **Schema Used**: IFC4 (default in IFCOpenShell)
- **Access Method**: `schema_by_name('IFC4')` returns schema object
- **Entity Enumeration**: `schema.entities()` returns 776 entities
- **Parent Access**: `entity.supertype()` returns single parent entity (or None for root)
- **Attributes**: `entity.all_attributes()` returns tuple of attribute objects

### Hierarchy Building Algorithm
1. Load all 776 entities from IFC4 schema
2. For each entity, call `.supertype()` to find parent
3. Build reverse mapping: parent → [children]
4. Identify roots: entities where `.supertype()` returns None
5. Recursively build nested tree structure from roots
6. Result: 59 root classes, 9 maximum depth, all 776 entities accounted for

### Class Relationship Properties
- **Direct Parent**: One parent per class (or None for root)
- **Direct Children**: Multiple possible
- **Subclasses**: All descendants recursively
- **Siblings**: Other children of the same parent
- **Depth**: Count of parent links to root

---

## Important Notes

### Case Sensitivity
- All IFC class names are **case-sensitive**
- ✓ Correct: `IfcWall`, `IfcElement`, `IfcProduct`
- ✗ Incorrect: `ifcwall`, `ifcelement`, `IFCWALL`

### Output Encoding
- All JSON files: UTF-8 encoding
- All text files: UTF-8 encoding
- BOM (Byte Order Mark): None

### Progress Reporting
- Progress messages written to stderr (not stdout)
- Allows clean piping: `python script.py | jq .`
- Errors also reported to stderr
- JSON output to stdout remains clean

### Data Consistency
- All scripts use same `get_ifc_classes()` function internally
- Ensures consistency across different output formats
- Flat list and hierarchy calculated from same source

### Caching Behavior
- Scripts do NOT cache between runs
- Each execution reloads all 776 entities from IFCOpenShell
- Typical first-run: 2-5 seconds
- Typical subsequent run: same (no in-memory caching between processes)
- Generated JSON files provide immediate reference without reloading

---

## Environment Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Installation
```bash
# Clone or navigate to project
cd c:\_LOCAL\GitHub\IFCXPrototype\server

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1  # PowerShell
# OR
.venv\Scripts\activate.bat   # Command Prompt

# Install IFCOpenShell
pip install ifcopenshell==0.8.4.post1

# Verify installation
python -c "import ifcopenshell; print(f'IFCOpenShell {ifcopenshell.version}')"
```

### Running Scripts

**Option 1: With virtual environment activated**
```bash
# Activate first
.venv\Scripts\Activate.ps1

# Then run
python generate_ifc_hierarchy.py
python ifc_hierarchy_query.py issubclass IfcWall IfcElement
```

**Option 2: Direct execution**
```bash
# No need to activate
.venv\Scripts\python.exe generate_ifc_hierarchy.py
.venv\Scripts\python.exe ifc_hierarchy_query.py issubclass IfcWall IfcElement
```

**Option 3: From any directory**
```powershell
# Using full path
C:\_LOCAL\GitHub\IFCXPrototype\server\.venv\Scripts\python.exe `
  C:\_LOCAL\GitHub\IFCXPrototype\server\utils\generate_ifc_hierarchy.py
```

### IDE Integration

**VS Code**
1. Open workspace in VS Code
2. Select Python interpreter: `.venv\Scripts\python.exe`
3. Run/Debug buttons will use correct environment

**PyCharm**
1. Project > Settings > Project > Python Interpreter
2. Click gear icon > Add
3. Select "Existing Environment" → `.venv\Scripts\python.exe`
4. Click OK

---

## File Format Examples

### JSON Pretty-Print
All scripts support pretty-printing for human readability:
```bash
# Standard (compact)
python ifc_descendants_export.py IfcWall

# Pretty-printed (indented)
python ifc_descendants_export.py IfcWall --pretty
```

### Text Tree Format Details
- Each line: one class name
- Indentation: tabs (not spaces) for hierarchy depth
- Encoding: UTF-8, no BOM
- Line ending: Generic (LF or CRLF)
- Sample:
  ```
  IfcRoot
  	IfcObjectDefinition
  		IfcContext
  			IfcProject
  ```

### Flat List Format
- JSON array of classes
- OR JSON object with metadata + classes
- Always includes: `name`, `parent`, `attributes`
- Sorted alphabetically by class name

### Schema Format
- Root classes listed as array
- Classes array with full attribute details
- Each attribute includes: `name`, `type`, `optional`, `derived`
- Types shown as string representation of type objects

---

## Notes

- All scripts load the IFC4 schema from IFCOpenShell (776 total entities)
- Execution time is typically 2-5 seconds depending on operation
- Output is UTF-8 encoded JSON
- Scripts report progress to stderr (not stdout), allowing clean piping
- All class names are case-sensitive (e.g., `IfcWall`, not `ifcwall`)

---

## Environment

```bash
# Activate virtual environment first
source .venv/Scripts/activate  # Linux/Mac
.venv\Scripts\activate.bat     # Windows CMD
.venv\Scripts\Activate.ps1     # Windows PowerShell

# Then run any script
python ifc_hierarchy_query.py issubclass IfcWall IfcElement
```

Or run directly:
```bash
.venv/Scripts/python.exe script_name.py [arguments]
```

