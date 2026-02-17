"""Flask server for IFC processing with file-based data store"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename

# Add ingestors to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestors'))

from ifc4ingestor import IFC2JSONSimple
from dataStores.fileBased import FileBasedStore
from memoryTree import MemoryTree

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'ifc', 'json'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize data store
file_store = FileBasedStore()

# Initialize memory tree
memory_tree = MemoryTree()

def refresh_memory_tree():
    """Refresh the in-memory component tree"""
    memory_tree.refresh_from_store(file_store.base_path)
    models = memory_tree.get_models()
    print(f"✅ Memory tree refreshed: {len(models)} model(s) loaded")
    return len(models)

# Refresh memory tree on startup
refresh_memory_tree()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def admin():
    """Serve the admin page"""
    return render_template('admin.html')

@app.route('/viewer')
def viewer():
    """Serve the advanced viewer page"""
    return render_template('viewer.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use .ifc or .json'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the uploaded file
        file.save(file_path)
        
        # Process based on file type
        if filename.lower().endswith('.ifc'):
            # Convert IFC to JSON using the ingestor
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
            
            converter = IFC2JSONSimple(file_path)
            json_objects = converter.spf2Json()
            
            # Save JSON temporarily
            with open(json_path, 'w') as f:
                json.dump(json_objects, f, indent=2, default=str)
            
            # Store in file-based data store
            result = file_store.store(json_filename, json_objects)
            
            # Refresh memory tree with new data
            refresh_memory_tree()
            
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
            
            # Store in file-based data store
            result = file_store.store(filename, json_objects)
            
            # Refresh memory tree with new data
            refresh_memory_tree()
            
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

@app.route('/api/status', methods=['GET'])
def status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '0.0.1'
    })

@app.route('/api/stores', methods=['GET'])
def list_stores():
    """List available data stores"""
    return jsonify([
        {
            'name': 'fileBased',
            'description': 'File-based data store'
        }
    ])

@app.route('/api/entityGuids', methods=['GET'])
def query_entity_guids():
    """Query for entity GUIDs
    
    Parameters:
    - models: comma-separated list of model names (optional)
    - entity_types: comma-separated list of entity types (optional)
    
    Returns: Dictionary mapping model names to arrays of entity GUIDs
    """
    try:
        # Parse query parameters
        models = request.args.get('models', '')
        entity_types = request.args.get('entity_types', '')
        
        models = [m.strip() for m in models.split(',')] if models else None
        entity_types = [t.strip() for t in entity_types.split(',')] if entity_types else None
        
        # If no specific models requested, use all available models
        if not models:
            models = memory_tree.get_models()
        
        # Query and organize results by model
        result_by_model = {}
        for model_name in models:
            entity_guids = memory_tree.get_entity_guids(
                models=[model_name],
                entity_types=entity_types
            )
            if entity_guids:
                result_by_model[model_name] = entity_guids
        
        return jsonify(result_by_model)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/componentGuids', methods=['GET'])
def query_component_guids():
    """Query for component GUIDs
    
    Parameters:
    - models: comma-separated list of model names (optional)
    - entity_guids: comma-separated list of entity GUIDs (optional)
    - entity_types: comma-separated list of entity types (optional)
    
    Returns: Dictionary mapping model names to arrays of component GUIDs
    """
    try:
        # Parse query parameters
        models = request.args.get('models', '')
        entity_guids = request.args.get('entity_guids', '')
        entity_types = request.args.get('entity_types', '')
        
        models = [m.strip() for m in models.split(',')] if models else None
        entity_guids = [e.strip() for e in entity_guids.split(',')] if entity_guids else None
        entity_types = [t.strip() for t in entity_types.split(',')] if entity_types else None
        
        # If no specific models requested, use all available models
        if not models:
            models = memory_tree.get_models()
        
        # Query and organize results by model
        result_by_model = {}
        for model_name in models:
            component_guids = memory_tree.get_component_guids(
                models=[model_name],
                entity_guids=entity_guids,
                entity_types=entity_types
            )
            if component_guids:
                result_by_model[model_name] = component_guids
        
        return jsonify(result_by_model)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/components', methods=['GET'])
def get_components():
    """Retrieve component data by GUIDs
    
    Parameters:
    - componentGuids: comma-separated list of component GUIDs
    
    Returns: Array of component dictionaries
    """
    try:
        # Parse query parameters
        component_guids = request.args.get('componentGuids', '')
        
        if not component_guids:
            return jsonify({'error': 'componentGuids parameter is required'}), 400
        
        component_guids = [g.strip() for g in component_guids.split(',')]
        
        # Retrieve components
        components = memory_tree.get_components(component_guids)
        
        return jsonify(components)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/refresh', methods=['POST'])
def refresh_memory():
    """Manually refresh the in-memory tree"""
    try:
        count = refresh_memory_tree()
        return jsonify({
            'models_loaded': count,
            'message': f'Memory tree refreshed with {count} model(s)'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """List all loaded models"""
    models = memory_tree.get_models()
    return jsonify(models)

@app.route('/api/entity_types', methods=['GET'])
def list_entity_types():
    """List all entity types in specified models
    
    Parameters:
    - models: comma-separated list of model names (optional)
    
    Returns: List of entity types
    """
    try:
        models = request.args.get('models', '')
        models = [m.strip() for m in models.split(',')] if models else None
        
        types = memory_tree.get_entity_types(models=models)
        
        return jsonify(types)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File is too large. Maximum size is 500MB'}), 413

if __name__ == '__main__':
    print("🚀 IFC Processing Server Starting...")
    print("📄 Admin Page: http://localhost:5000")
    print("🔍 Viewer Page: http://localhost:5000/viewer")
    print("\n📡 API Endpoints:")
    print("   POST   /api/upload                  - Upload & process IFC/JSON files")
    print("   GET    /api/entityGuids             - Query entity GUIDs")
    print("   GET    /api/componentGuids         - Query component GUIDs")
    print("   GET    /api/components              - Retrieve component data")
    print("   GET    /api/models                  - List all models")
    print("   GET    /api/entity_types            - List entity types")
    print("   POST   /api/refresh                 - Manually refresh memory tree")
    print("   GET    /api/status                  - Server status")
    print("\n📁 Uploads: " + os.path.abspath(UPLOAD_FOLDER))
    print("💾 Data Store: " + os.path.abspath(file_store.base_path))
    print("\n" + "="*50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
