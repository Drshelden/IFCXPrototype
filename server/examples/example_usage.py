"""Example: Using the IFC Processing Server with File-Based Backend

This example shows how to:
1. Initialize the server with file-based storage
2. Store components
3. Query components
"""

import os
import sys

# Add server to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import IFCProcessingServer, create_app

def example_basic_usage():
    """Basic usage example"""
    print("\n" + "="*50)
    print("Example 1: Basic Server Usage")
    print("="*50)
    
    # Create server with file-based backend
    server = IFCProcessingServer(data_store_type='fileBased')
    
    # Access components
    print(f"\nData Store Type: {server.data_store_type}")
    print(f"File Store Path: {server.file_store.base_path}")
    print(f"Models Loaded: {server.memory_tree.get_models()}")
    
    return server

def example_factory_function():
    """Using the factory function"""
    print("\n" + "="*50)
    print("Example 2: Using Factory Function")
    print("="*50)
    
    # Create Flask app with factory function
    app = create_app(data_store_type='fileBased')
    
    print(f"\nFlask app created: {app}")
    print(f"Data Store Type: {app.config['DATA_STORE_TYPE']}")
    
    # Access config
    print(f"Config: {dict(app.config)}")
    
    return app

def example_backend_switching():
    """Show how backends can be switched"""
    print("\n" + "="*50)
    print("Example 3: Backend Switching")
    print("="*50)
    
    # File-based backend
    print("\nCreating file-based server...")
    server_file = IFCProcessingServer(data_store_type='fileBased')
    print(f"Backend: {server_file.data_store_type}")
    print(f"Memory Tree Type: {type(server_file.memory_tree).__name__}")
    
    # MongoDB backend (stub)
    print("\nCreating MongoDB server (stub)...")
    try:
        server_mongo = IFCProcessingServer(data_store_type='mongodbBased')
        print(f"Backend: {server_mongo.data_store_type}")
        print(f"Memory Tree Type: {type(server_mongo.memory_tree).__name__}")
    except NotImplementedError as e:
        print(f"MongoDB not yet implemented: {e}")

def example_query_components():
    """Show how to query components"""
    print("\n" + "="*50)
    print("Example 4: Querying Components")
    print("="*50)
    
    server = IFCProcessingServer(data_store_type='fileBased')
    
    # Get all models
    models = server.memory_tree.get_models()
    print(f"\nLoaded Models: {models}")
    
    if models:
        # Query first model
        model_name = models[0]
        print(f"\nQuerying model: {model_name}")
        
        # Get entity GUIDs
        entity_guids = server.memory_tree.get_entity_guids(models=[model_name])
        print(f"  Entities: {len(entity_guids)} (showing first 5)")
        for guid in entity_guids[:5]:
            print(f"    - {guid}")
        
        # Get component GUIDs
        component_guids = server.memory_tree.get_component_guids(models=[model_name])
        print(f"\n  Components: {len(component_guids)} (showing first 5)")
        for guid in component_guids[:5]:
            print(f"    - {guid}")
        
        # Get entity types
        entity_types = server.memory_tree.get_entity_types(models=[model_name])
        print(f"\n  Entity Types: {entity_types}")
    else:
        print("\n⚠️  No models loaded. Upload some data first.")

def example_environment_config():
    """Show how environment variables control backend selection"""
    print("\n" + "="*50)
    print("Example 5: Environment Configuration")
    print("="*50)
    
    # Current environment
    current_backend = os.environ.get('IFC_DATA_STORE', 'fileBased')
    print(f"\nCurrent IFC_DATA_STORE: {current_backend}")
    
    # Show how to set it
    print("\nTo set backend via environment variable:")
    print("  Windows CMD:")
    print("    set IFC_DATA_STORE=fileBased")
    print("    python server.py")
    print("\n  Windows PowerShell:")
    print("    $env:IFC_DATA_STORE='fileBased'")
    print("    python server.py")
    print("\n  Linux/Mac:")
    print("    export IFC_DATA_STORE=fileBased")
    print("    python server.py")

def example_api_testing():
    """Show how to test the API"""
    print("\n" + "="*50)
    print("Example 6: API Testing with Flask Test Client")
    print("="*50)
    
    # Create server
    server = IFCProcessingServer(data_store_type='fileBased')
    
    # Use Flask test client
    client = server.app.test_client()
    
    # Test endpoints
    print("\nTesting API endpoints:")
    
    # Get status
    response = client.get('/api/status')
    print(f"\nGET /api/status")
    print(f"  Status: {response.status_code}")
    print(f"  Data: {response.json}")
    
    # Get stores
    response = client.get('/api/stores')
    print(f"\nGET /api/stores")
    print(f"  Status: {response.status_code}")
    print(f"  Stores: {[s['name'] for s in response.json]}")
    
    # Get models
    response = client.get('/api/models')
    print(f"\nGET /api/models")
    print(f"  Status: {response.status_code}")
    print(f"  Models: {response.json}")

def example_custom_backend():
    """Example of how you would use a custom backend"""
    print("\n" + "="*50)
    print("Example 7: Custom Backend Pattern")
    print("="*50)
    
    print("""
To implement a custom backend (e.g., PostgreSQL):

1. Create backend directory structure:
   dataStores/postgresqlBased/
   ├── __init__.py
   ├── postgresqlBased.py
   └── postgresqlMemoryTree.py

2. Implement required classes:
   - PostgreSQLStore (implements store(), retrieve(), list_directories())
   - PostgreSQLMemoryTree (implements get_entity_guids(), get_component_guids(), etc.)

3. Update server.py initialization:
   elif self.data_store_type == 'postgresqlBased':
       from postgresqlBased import PostgreSQLStore, PostgreSQLMemoryTree
       self.file_store = PostgreSQLStore()
       self.memory_tree = PostgreSQLMemoryTree(self.file_store)

4. Use it:
   server = IFCProcessingServer(data_store_type='postgresqlBased')

See BACKEND_INTERFACE.md for full implementation guide.
    """)

def main():
    """Run all examples"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     IFC Processing Server - Usage Examples                   ║
║     Reorganized Architecture with Pluggable Backends          ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Run examples
    example_basic_usage()
    example_factory_function()
    example_backend_switching()
    example_query_components()
    example_environment_config()
    example_api_testing()
    example_custom_backend()
    
    print("\n" + "="*50)
    print("Examples complete!")
    print("="*50 + "\n")
    
    print("Documentation:")
    print("  - REORGANIZATION.md  - Full architecture overview")
    print("  - QUICK_START.md     - Quick start guide")
    print("  - BACKEND_INTERFACE.md - How to implement backends")
    print("\nNext Steps:")
    print("  1. python ifcxServerFileStore.py  # Start the server")
    print("  2. http://localhost:5000          # Open admin interface")
    print("  3. Upload IFC files to test the system")

if __name__ == '__main__':
    main()
