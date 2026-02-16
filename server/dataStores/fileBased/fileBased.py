"""File-based data store for IFC components"""

import os
import json
from pathlib import Path

class FileBasedStore:
    """Store components in a file-based directory structure"""
    
    def __init__(self, base_path=None):
        """Initialize the file-based store
        
        Args:
            base_path: Base directory for the data store. Defaults to 'dataStores/fileBased/data'
        """
        if base_path is None:
            base_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'dataStores',
                'fileBased',
                'data'
            )
        
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
    
    def store(self, filename, components):
        """Store components from a file
        
        Args:
            filename: Name of the source file (used to create directory)
            components: List of component dictionaries
            
        Returns:
            Dictionary with store result information
        """
        # Create directory name from filename (remove extension)
        dir_name = os.path.splitext(filename)[0]
        dir_path = os.path.join(self.base_path, dir_name)
        
        # Create the directory
        os.makedirs(dir_path, exist_ok=True)
        
        # Store each component as a separate file
        stored_count = 0
        
        for component in components:
            # Get entityGuid and guid from component
            entity_guid = component.get('entityGuid', 'unknown')
            guid = component.get('guid', 'unknown')
            
            # Create filename: entityGuid_guid.json
            component_filename = f"{entity_guid}_{guid}.json"
            component_path = os.path.join(dir_path, component_filename)
            
            # Write component to file
            try:
                with open(component_path, 'w') as f:
                    json.dump(component, f, indent=2, default=str)
                stored_count += 1
            except Exception as e:
                print(f"Error storing component {component_filename}: {e}")
        
        return {
            'success': True,
            'count': stored_count,
            'path': dir_path,
            'directory': dir_name
        }
    
    def retrieve(self, directory):
        """Retrieve all components from a directory
        
        Args:
            directory: Directory name to retrieve from
            
        Returns:
            List of component dictionaries
        """
        dir_path = os.path.join(self.base_path, directory)
        
        if not os.path.isdir(dir_path):
            return []
        
        components = []
        
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                file_path = os.path.join(dir_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        component = json.load(f)
                        components.append(component)
                except Exception as e:
                    print(f"Error reading component {filename}: {e}")
        
        return components
    
    def list_directories(self):
        """List all stored directories
        
        Returns:
            List of directory names
        """
        if not os.path.isdir(self.base_path):
            return []
        
        directories = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                # Count JSON files in directory
                json_files = [f for f in os.listdir(item_path) if f.endswith('.json')]
                directories.append({
                    'name': item,
                    'component_count': len(json_files)
                })
        
        return directories
