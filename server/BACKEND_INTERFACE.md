# Backend Interface & Implementation Guide

This guide explains how to implement new data store backends for the IFC Processing Server.

## Backend Contract

Every data store backend must implement these two interfaces:

### 1. Data Store Interface

```python
class YourDataStore:
    """Base data store interface"""
    
    def store(self, filename: str, components: List[Dict]) -> Dict:
        """Store components from a file
        
        Args:
            filename: Source filename (used for model naming)
            components: List of component dictionaries to store
                Each component should have:
                - componentGuid: Unique identifier
                - entityGuid: Parent entity identifier
                - componentType: Type of component
                - entityType: Type of entity
                - ... (other fields preserved)
        
        Returns:
            {
                'success': bool,
                'count': int,              # Components stored
                'path': str,               # Store path/location
                'directory': str           # Model/collection name
            }
        """
        pass
    
    def retrieve(self, directory: str) -> List[Dict]:
        """Retrieve all components from a model/directory
        
        Args:
            directory: Model/collection name
            
        Returns:
            List of component dictionaries
        """
        pass
    
    def list_directories(self) -> List[Dict]:
        """List all stored models/collections
        
        Returns:
            [
                {
                    'name': str,
                    'component_count': int,
                    'created': datetime (optional),
                    'modified': datetime (optional)
                },
                ...
            ]
        """
        pass
```

### 2. Memory Tree Interface

```python
class YourMemoryTree:
    """Query engine interface"""
    
    def refresh(self) -> int:
        """Refresh memory tree from data store
        
        Returns:
            Number of models loaded
        """
        pass
    
    def get_entity_guids(self, 
                        models: Optional[List[str]] = None,
                        entity_types: Optional[List[str]] = None,
                        components: Optional[List[str]] = None) -> List[str]:
        """Query for entity GUIDs
        
        Args:
            models: Filter by model names (None = all)
            entity_types: Filter by entity types (None = all)
            components: Filter by component GUIDs (None = all)
        
        Returns:
            Sorted list of entity GUIDs matching filters
        """
        pass
    
    def get_component_guids(self,
                           models: Optional[List[str]] = None,
                           entity_guids: Optional[List[str]] = None,
                           entity_types: Optional[List[str]] = None) -> List[str]:
        """Query for component GUIDs
        
        Args:
            models: Filter by model names (None = all)
            entity_guids: Filter by entity GUIDs (None = all)
            entity_types: Filter by entity types (None = all)
        
        Returns:
            Sorted list of component GUIDs matching filters
        """
        pass
    
    def get_components(self, guids: List[str], 
                      models: Optional[List[str]] = None) -> List[Dict]:
        """Retrieve component data by GUIDs
        
        Args:
            guids: Component GUIDs to retrieve
            models: Limit search to models (None = search all)
        
        Returns:
            List of component dictionaries
            Each component must include 'model' field with the model name
        """
        pass
    
    def get_models(self) -> List[str]:
        """Get list of all loaded models
        
        Returns:
            Sorted list of model names
        """
        pass
    
    def get_entity_types(self, models: Optional[List[str]] = None) -> List[str]:
        """Get list of entity types
        
        Args:
            models: Filter by model names (None = all)
        
        Returns:
            Sorted list of entity types
        """
        pass
```

## Implementation Example: PostgreSQL Backend

Here's how you would implement a PostgreSQL backend:

### 1. Create Backend Directory

```
dataStores/postgresqlBased/
├── __init__.py
├── postgresqlBased.py
└── postgresqlMemoryTree.py
```

### 2. Implement Data Store

```python
# dataStores/postgresqlBased/postgresqlBased.py

import psycopg2
from datetime import datetime
from typing import List, Dict, Optional

class PostgreSQLStore:
    """PostgreSQL data store implementation"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize PostgreSQL store
        
        Args:
            connection_string: PostgreSQL connection URL
                Default: postgresql://user:password@localhost/ifc_components
        """
        self.connection_string = connection_string or \
            'postgresql://postgres:password@localhost/ifc_components'
        self.connection = None
        self.connect()
        self._init_schema()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        self.connection = psycopg2.connect(self.connection_string)
        print(f"✅ Connected to PostgreSQL: {self.connection_string}")
    
    def _init_schema(self):
        """Initialize database schema if needed"""
        with self.connection.cursor() as cursor:
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    component_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    modified_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS components (
                    id SERIAL PRIMARY KEY,
                    model_id INT REFERENCES models(id),
                    component_guid VARCHAR(255) NOT NULL,
                    entity_guid VARCHAR(255),
                    component_type VARCHAR(255),
                    entity_type VARCHAR(255),
                    data JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(model_id, component_guid)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS 
                idx_components_entity_guid ON components(entity_guid)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS 
                idx_components_entity_type ON components(entity_type)
            ''')
            
            self.connection.commit()
    
    def store(self, filename: str, components: List[Dict]) -> Dict:
        """Store components with PostgreSQL"""
        # Extract model name from filename
        model_name = os.path.splitext(filename)[0]
        
        with self.connection.cursor() as cursor:
            # Insert or update model
            cursor.execute('''
                INSERT INTO models (name, component_count)
                VALUES (%s, %s)
                ON CONFLICT (name) DO UPDATE 
                SET component_count = %s, modified_at = NOW()
            ''', (model_name, len(components), len(components)))
            
            # Get model ID
            cursor.execute('SELECT id FROM models WHERE name = %s', (model_name,))
            model_id = cursor.fetchone()[0]
            
            # Insert components
            stored_count = 0
            for component in components:
                try:
                    cursor.execute('''
                        INSERT INTO components 
                        (model_id, component_guid, entity_guid, 
                         component_type, entity_type, data)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (
                        model_id,
                        component.get('componentGuid'),
                        component.get('entityGuid'),
                        component.get('componentType'),
                        component.get('entityType'),
                        json.dumps(component)
                    ))
                    stored_count += 1
                except Exception as e:
                    print(f"Error storing component: {e}")
            
            self.connection.commit()
        
        return {
            'success': True,
            'count': stored_count,
            'path': f'postgresql://{self.connection_string}',
            'directory': model_name
        }
    
    def retrieve(self, directory: str) -> List[Dict]:
        """Retrieve components from PostgreSQL"""
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT data FROM components
                JOIN models ON components.model_id = models.id
                WHERE models.name = %s
            ''', (directory,))
            
            components = []
            for (data,) in cursor.fetchall():
                components.append(json.loads(data))
            
            return components
    
    def list_directories(self) -> List[Dict]:
        """List all models in PostgreSQL"""
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT name, component_count, created_at, modified_at
                FROM models
                ORDER BY name
            ''')
            
            directories = []
            for (name, count, created, modified) in cursor.fetchall():
                directories.append({
                    'name': name,
                    'component_count': count,
                    'created': created,
                    'modified': modified
                })
            
            return directories
```

### 3. Implement Memory Tree

```python
# dataStores/postgresqlBased/postgresqlMemoryTree.py

class PostgreSQLMemoryTree:
    """Query engine for PostgreSQL backend"""
    
    def __init__(self, store: PostgreSQLStore):
        self.store = store
        self.models_cache = {}
    
    def refresh(self) -> int:
        """Refresh memory tree from PostgreSQL"""
        # Load model metadata
        models = self.store.list_directories()
        self.models_cache = {m['name']: m for m in models}
        return len(self.models_cache)
    
    def get_entity_guids(self, 
                        models: Optional[List[str]] = None,
                        entity_types: Optional[List[str]] = None,
                        components: Optional[List[str]] = None) -> List[str]:
        """Query entity GUIDs from PostgreSQL"""
        with self.store.connection.cursor() as cursor:
            # Build query
            query = '''
                SELECT DISTINCT entity_guid FROM components
                JOIN models ON components.model_id = models.id
                WHERE 1=1
            '''
            params = []
            
            if models:
                query += f" AND models.name IN ({','.join(['%s']*len(models))})"
                params.extend(models)
            
            if entity_types:
                query += f" AND entity_type IN ({','.join(['%s']*len(entity_types))})"
                params.extend(entity_types)
            
            if components:
                query += f" AND component_guid IN ({','.join(['%s']*len(components))})"
                params.extend(components)
            
            query += " ORDER BY entity_guid"
            
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]
    
    # ... implement other methods similarly ...
```

### 4. Register in server.py

```python
def _initialize_backend(self):
    """Initialize the selected data store backend"""
    # ... existing code ...
    elif self.data_store_type == 'postgresqlBased':
        from postgresqlBased import PostgreSQLStore
        from postgresqlMemoryTree import PostgreSQLMemoryTree
        
        self.file_store = PostgreSQLStore()
        self.memory_tree = PostgreSQLMemoryTree(self.file_store)
        
        print(f"✅ Initialized PostgreSQL data store")
```

## Testing Your Backend

### Unit Test Template

```python
# tests/test_postgresql_backend.py

import pytest
from dataStores.postgresqlBased import PostgreSQLStore, PostgreSQLMemoryTree

@pytest.fixture
def store():
    return PostgreSQLStore('postgresql://test:test@localhost/test_db')

@pytest.fixture
def memory_tree(store):
    tree = PostgreSQLMemoryTree(store)
    tree.refresh()
    return tree

def test_store_components(store):
    components = [
        {
            'componentGuid': 'guid-1',
            'entityGuid': 'entity-1',
            'componentType': 'WallComponent',
            'entityType': 'IfcWall'
        }
    ]
    
    result = store.store('TestModel', components)
    assert result['success']
    assert result['count'] == 1

def test_query_components(memory_tree):
    guids = memory_tree.get_entity_guids()
    assert len(guids) > 0
```

## Performance Considerations

- **Indexing**: Create indexes on frequently queried fields (entity_guid, entity_type)
- **Caching**: Implement memory caching layer for repeated queries
- **Pagination**: For large datasets, implement pagination to limit results
- **Connection Pooling**: Use connection pooling for database backends
- **Lazy Loading**: Load models on-demand rather than all at startup

## Migration from File-Based

If switching from file-based to PostgreSQL:

```python
# Migrate components from files to PostgreSQL
from dataStores.fileBased import FileBasedStore as OldStore
from dataStores.postgresqlBased import PostgreSQLStore as NewStore

old_store = OldStore()
new_store = NewStore()

for model_dir in old_store.list_directories():
    model_name = model_dir['name']
    components = old_store.retrieve(model_name)
    new_store.store(model_name + '.json', components)
    print(f"Migrated {model_name}: {len(components)} components")
```

## Debugging Backend Issues

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MyDataStore:
    def store(self, filename, components):
        logger.debug(f"Storing {len(components)} components from {filename}")
        # ...
```

### Test Backend Directly

```python
from dataStores.postgresqlBased import PostgreSQLStore, PostgreSQLMemoryTree

# Test store
store = PostgreSQLStore()
components = [{'componentGuid': 'test', ...}]
result = store.store('TestModel', components)
print(result)

# Test queries
tree = PostgreSQLMemoryTree(store)
tree.refresh()
models = tree.get_models()
print(f"Models: {models}")
```

---

For more information, see the main [REORGANIZATION.md](./REORGANIZATION.md) document.
