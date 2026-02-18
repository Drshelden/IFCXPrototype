"""Core Flask server for IFC processing with pluggable data store backends"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Add ingestors to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestors'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dataStores', 'fileBased'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dataStores', 'mongodbBased'))

from ifc4ingestor import IFC2JSONSimple


class IFCProcessingServer:
    """Core IFC Processing Server with pluggable data store backends"""
    
    def __init__(self, data_store_type='fileBased'):
        """Initialize the server with specified data store backend
        
        Args:
            data_store_type: 'fileBased' or 'mongodbBased'
        """
        self.data_store_type = data_store_type
        self.app = Flask(__name__)
        self.file_store = None
        self.memory_tree = None
        
        # Configure Flask app
        self._configure_app()
        
        # Initialize data store and memory tree based on type
        self._initialize_backend()
        
        # Register routes
        self._register_routes()
    
    def _configure_app(self):
        """Configure Flask application"""
        # Enable CORS for all routes
        CORS(self.app)
        
        # Configuration
        UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
        ALLOWED_EXTENSIONS = {'ifc', 'json'}
        MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
        
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        self.app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
        self.app.config['DATA_STORE_TYPE'] = self.data_store_type
        
        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Store config for use in route handlers
        self.upload_folder = UPLOAD_FOLDER
        self.allowed_extensions = ALLOWED_EXTENSIONS
    
    def _initialize_backend(self):
        """Initialize the selected data store backend"""
        if self.data_store_type == 'fileBased':
            from fileBased import FileBasedStore
            from memoryTree import MemoryTree
            
            self.file_store = FileBasedStore()
            self.memory_tree = MemoryTree()
            
            # Refresh memory tree on startup
            self._refresh_memory_tree()
            print(f"✅ Initialized file-based data store at: {self.file_store.base_path}")
            
        elif self.data_store_type == 'mongodbBased':
            from mongodbBased import MongoDBStore
            from mongodbMemoryTree import MongoDBMemoryTree
            
            self.file_store = MongoDBStore()
            self.memory_tree = MongoDBMemoryTree()
            
            print(f"✅ Initialized MongoDB data store")
        else:
            raise ValueError(f"Unknown data store type: {self.data_store_type}")
    
    def _refresh_memory_tree(self):
        """Refresh the in-memory component tree"""
        try:
            if self.data_store_type == 'fileBased':
                self.memory_tree.refresh_from_store(self.file_store.base_path)
                models = self.memory_tree.get_models()
                print(f"✅ Memory tree refreshed: {len(models)} model(s) loaded")
                return len(models)
            else:
                # MongoDB backend handles its own refresh
                return self.memory_tree.refresh()
        except Exception as e:
            print(f"❌ Error refreshing memory tree: {e}")
            return 0
    
    def _allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.app.config.get('ALLOWED_EXTENSIONS', [])
    
    def _register_routes(self):
        """Register all Flask routes"""
        
        @self.app.route('/')
        def admin():
            """Serve the admin page"""
            return render_template('admin.html')
        
        @self.app.route('/viewer')
        def viewer():
            """Serve the advanced viewer page"""
            return render_template('viewer.html')
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload_file():
            """Handle file upload and processing"""
            try:
                # Check if file is in request
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not self._allowed_file(file.filename):
                    return jsonify({'error': 'File type not allowed. Use .ifc or .json'}), 400
                
                # Secure the filename
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.upload_folder, filename)
                
                # Save the uploaded file
                file.save(file_path)
                
                # Process based on file type
                if filename.lower().endswith('.ifc'):
                    # Convert IFC to JSON using the ingestor
                    json_filename = os.path.splitext(filename)[0] + '.json'
                    json_path = os.path.join(self.upload_folder, json_filename)
                    
                    converter = IFC2JSONSimple(file_path)
                    json_objects = converter.spf2Json()
                    
                    # Save JSON temporarily
                    with open(json_path, 'w') as f:
                        json.dump(json_objects, f, indent=2, default=str)
                    
                    # Store in data store
                    result = self.file_store.store(json_filename, json_objects)
                    
                    # Refresh memory tree with new data
                    self._refresh_memory_tree()
                    
                    # Clean up uploads
                    os.remove(file_path)
                    os.remove(json_path)
                    
                    return jsonify({
                        'filename': json_filename,
                        'entities_count': len(json_objects),
                        'stored_count': result.get('count', 0),
                        'store_path': result.get('path', ''),
                        'message': f"Successfully processed {len(json_objects)} entities"
                    })
                
                elif filename.lower().endswith('.json'):
                    # Load JSON and store
                    with open(file_path, 'r') as f:
                        json_objects = json.load(f)
                    
                    if not isinstance(json_objects, list):
                        return jsonify({'error': 'JSON file must contain an array of components'}), 400
                    
                    # Store in data store
                    result = self.file_store.store(filename, json_objects)
                    
                    # Refresh memory tree with new data
                    self._refresh_memory_tree()
                    
                    # Clean up upload
                    os.remove(file_path)
                    
                    return jsonify({
                        'filename': filename,
                        'entities_count': len(json_objects),
                        'stored_count': result.get('count', 0),
                        'store_path': result.get('path', ''),
                        'message': f"Successfully stored {len(json_objects)} entities"
                    })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """Get server status"""
            return jsonify({
                'status': 'running',
                'data_store': self.data_store_type,
                'timestamp': datetime.now().isoformat(),
                'version': '0.1.0'
            })
        
        @self.app.route('/api/stores', methods=['GET'])
        def list_stores():
            """List available data stores"""
            return jsonify([
                {
                    'name': 'fileBased',
                    'description': 'File-based data store',
                    'status': 'active' if self.data_store_type == 'fileBased' else 'available'
                },
                {
                    'name': 'mongodbBased',
                    'description': 'MongoDB-based data store',
                    'status': 'active' if self.data_store_type == 'mongodbBased' else 'available'
                }
            ])
        
        @self.app.route('/api/entityGuids', methods=['GET'])
        def query_entity_guids():
            """Query for entity GUIDs
            
            Parameters:
            - models: comma-separated list of model names (optional)
            - entityTypes: comma-separated list of entity types (optional)
            
            Returns: Dictionary mapping model names to arrays of entity GUIDs
            """
            try:
                # Parse query parameters
                models = request.args.get('models', '')
                entity_types = request.args.get('entityTypes', '')
                
                models = [m.strip() for m in models.split(',')] if models else None
                entity_types = [t.strip() for t in entity_types.split(',')] if entity_types else None
                
                # If no specific models requested, use all available models
                if not models:
                    models = self.memory_tree.get_models()
                
                # Query and organize results by model
                result_by_model = {}
                for model_name in models:
                    entity_guids = self.memory_tree.get_entity_guids(
                        models=[model_name],
                        entity_types=entity_types
                    )
                    if entity_guids:
                        result_by_model[model_name] = entity_guids
                
                return jsonify(result_by_model)
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/componentGuids', methods=['GET'])
        def query_component_guids():
            """Query for component GUIDs
            
            Parameters:
            - models: comma-separated list of model names (optional)
            - entityGuids: comma-separated list of entity GUIDs (optional)
            - entityTypes: comma-separated list of entity types (optional)
            
            Returns: Dictionary mapping model names to arrays of component GUIDs
            """
            try:
                # Parse query parameters
                models = request.args.get('models', '')
                entity_guids = request.args.get('entityGuids', '')
                entity_types = request.args.get('entityTypes', '')
                
                models = [m.strip() for m in models.split(',')] if models else None
                entity_guids = [e.strip() for e in entity_guids.split(',')] if entity_guids else None
                entity_types = [t.strip() for t in entity_types.split(',')] if entity_types else None
                
                # If no specific models requested, use all available models
                if not models:
                    models = self.memory_tree.get_models()
                
                # Query and organize results by model
                result_by_model = {}
                for model_name in models:
                    component_guids = self.memory_tree.get_component_guids(
                        models=[model_name],
                        entity_guids=entity_guids,
                        entity_types=entity_types
                    )
                    if component_guids:
                        result_by_model[model_name] = component_guids
                
                return jsonify(result_by_model)
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/components', methods=['GET'])
        def get_components():
            """Retrieve component data with flexible filtering, organized by model
            
            Parameters:
            - componentGuids: comma-separated list of specific component GUIDs (optional)
            - models: comma-separated list of model names (optional)
            - entityTypes: comma-separated list of entity types (optional)
            - entityGuids: comma-separated list of entity GUIDs (optional)
            
            Returns: Dictionary mapping model names to arrays of component objects
            """
            try:
                # Parse query parameters
                component_guids_param = request.args.get('componentGuids', '')
                models = request.args.get('models', '')
                entity_types = request.args.get('entityTypes', '')
                entity_guids = request.args.get('entityGuids', '')
                
                # Parse into lists
                component_guids = [g.strip() for g in component_guids_param.split(',')] if component_guids_param else None
                models = [m.strip() for m in models.split(',')] if models else None
                entity_types = [t.strip() for t in entity_types.split(',')] if entity_types else None
                entity_guids = [g.strip() for g in entity_guids.split(',')] if entity_guids else None
                
                print(f"\n📋 /api/components query:")
                print(f"   componentGuids: {component_guids}")
                print(f"   models: {models}")
                print(f"   entityTypes: {entity_types}")
                print(f"   entityGuids: {entity_guids}")
                
                # If specific component GUIDs provided, use those directly
                if component_guids:
                    components = self.memory_tree.get_components(component_guids)
                # Otherwise, use query filters to find components
                elif models or entity_types or entity_guids:
                    # Query component GUIDs based on filters
                    found_guids = self.memory_tree.get_component_guids(
                        models=models,
                        entity_types=entity_types,
                        entity_guids=entity_guids
                    )
                    # Get components, restricting search to the filtered models
                    components = self.memory_tree.get_components(found_guids, models=models)
                else:
                    # No filters specified - return all components from all models
                    all_guids = self.memory_tree.get_component_guids()
                    components = self.memory_tree.get_components(all_guids)
                
                print(f"   Returned {len(components)} components")
                
                # Organize components by model
                result_by_model = {}
                for component in components:
                    model_name = component.get('model') or component.get('componentGuid', '')
                    if model_name not in result_by_model:
                        result_by_model[model_name] = []
                    result_by_model[model_name].append(component)
                
                print(f"   Organized into {len(result_by_model)} models: {list(result_by_model.keys())}")
                
                return jsonify(result_by_model)
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/refresh', methods=['POST'])
        def refresh_memory():
            """Manually refresh the in-memory tree"""
            try:
                count = self._refresh_memory_tree()
                return jsonify({
                    'models_loaded': count,
                    'message': f'Memory tree refreshed with {count} model(s)'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/models', methods=['GET'])
        def list_models():
            """List all loaded models"""
            models = self.memory_tree.get_models()
            return jsonify(models)
        
        @self.app.route('/api/entityTypes', methods=['GET'])
        def list_entity_types():
            """List all entity types in specified models
            
            Parameters:
            - models: comma-separated list of model names (optional)
            
            Returns: List of entity types
            """
            try:
                models = request.args.get('models', '')
                models = [m.strip() for m in models.split(',')] if models else None
                
                types = self.memory_tree.get_entity_types(models=models)
                
                return jsonify(types)
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.errorhandler(413)
        def too_large(e):
            """Handle file too large error"""
            return jsonify({'error': 'File is too large. Maximum size is 500MB'}), 413


def create_app(data_store_type='fileBased'):
    """Factory function to create and configure the Flask app
    
    Args:
        data_store_type: 'fileBased' or 'mongodbBased'
    
    Returns:
        Flask application instance
    """
    server = IFCProcessingServer(data_store_type=data_store_type)
    return server.app


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='IFC Processing Server with pluggable data store backends',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python server.py                    # Use default file-based backend
  python server.py --backend fileBased
  python server.py --backend mongodbBased
  python server.py -b fileBased --port 5001
  python server.py --help
        '''
    )
    
    parser.add_argument(
        '--backend', '-b',
        choices=['fileBased', 'mongodbBased'],
        default='fileBased',
        help='Data store backend to use (default: fileBased)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='Port to listen on (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable Flask debug mode'
    )
    
    args = parser.parse_args()
    
    # Validate backend choice
    if args.backend not in ['fileBased', 'mongodbBased']:
        print(f"❌ Unknown backend: {args.backend}")
        print("Available backends: fileBased, mongodbBased")
        sys.exit(1)
    
    # Create server
    server = IFCProcessingServer(data_store_type=args.backend)
    
    print("🚀 IFC Processing Server Starting...")
    print(f"💾 Data Store: {args.backend}")
    print(f"🌐 Host: {args.host}:{args.port}")
    print("📄 Admin Page: http://localhost:{}/".format(args.port) if args.host == '0.0.0.0' else f"http://{args.host}:{args.port}/")
    print("🔍 Viewer Page: http://localhost:{}/viewer".format(args.port) if args.host == '0.0.0.0' else f"http://{args.host}:{args.port}/viewer")
    print("\n📡 API Endpoints:")
    print("   POST   /api/upload                  - Upload & process IFC/JSON files")
    print("   GET    /api/entityGuids             - Query entity GUIDs")
    print("   GET    /api/componentGuids         - Query component GUIDs")
    print("   GET    /api/components              - Retrieve component data")
    print("   GET    /api/models                  - List all models")
    print("   GET    /api/entityTypes             - List entity types")
    print("   GET    /api/stores                  - List available data stores")
    print("   POST   /api/refresh                 - Manually refresh memory tree")
    print("   GET    /api/status                  - Server status")
    print("\n📁 Uploads: " + os.path.abspath(server.upload_folder))
    
    if args.backend == 'fileBased' and server.file_store:
        print("💾 File Store: " + os.path.abspath(server.file_store.base_path))
    
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        server.app.run(debug=args.debug, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        sys.exit(0)
