"""In-memory tree structure for component storage and querying"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set

class MemoryTree:
    """In-memory tree structure for fast component querying"""
    
    def __init__(self):
        """Initialize the memory tree"""
        self.models: Dict = {}  # models[model_name] = {by_entity, by_type, by_componentGuid}
    
    def refresh_from_store(self, store_path: str):
        """Refresh memory tree from file-based store
        
        Args:
            store_path: Path to the file-based data store
        """
        self.models = {}
        
        if not os.path.isdir(store_path):
            return
        
        # Iterate through each model directory
        for model_name in os.listdir(store_path):
            model_path = os.path.join(store_path, model_name)
            
            if not os.path.isdir(model_path):
                continue
            
            # Initialize model structure
            self.models[model_name] = {
                'by_entity': {},      # entity_guid -> [componentGuids]
                'by_type': {},        # component_type -> [componentGuids]
                'by_componentGuid': {}         # componentGuid -> component_data
            }
            
            # Load all components for this model
            for filename in os.listdir(model_path):
                if not filename.endswith('.json'):
                    continue
                
                component_path = os.path.join(model_path, filename)
                try:
                    with open(component_path, 'r') as f:
                        component = json.load(f)
                    
                    # Get component GUID
                    component_guid = component.get('componentGuid')
                    if not component_guid:
                        continue
                    
                    # Store by GUID
                    self.models[model_name]['by_componentGuid'][component_guid] = component
                    
                    # Index by entity GUID
                    entity_guid = component.get('entityGuid')
                    if entity_guid:
                        if entity_guid not in self.models[model_name]['by_entity']:
                            self.models[model_name]['by_entity'][entity_guid] = []
                        self.models[model_name]['by_entity'][entity_guid].append(component_guid)
                    
                    # Index by component type (remove trailing "Component")
                    component_type = component.get('componentType', 'Unknown')
                    if component_type.endswith('Component'):
                        component_type = component_type[:-9]  # Remove 'Component'
                    
                    if component_type not in self.models[model_name]['by_type']:
                        self.models[model_name]['by_type'][component_type] = []
                    self.models[model_name]['by_type'][component_type].append(component_guid)
                    
                except Exception as e:
                    print(f"Error loading component {filename}: {e}")
    
    def get_entity_guids(self, 
                        models: Optional[List[str]] = None,
                        entity_types: Optional[List[str]] = None,
                        components: Optional[List[str]] = None) -> List[str]:
        """Query for entity GUIDs
        
        Args:
            models: List of model names (None = all models)
            entity_types: List of entity types to filter by (None = all types)
            components: List of component GUIDs to filter by (None = all components)
            
        Returns:
            List of entity GUIDs matching the criteria
        """
        # Determine which models to search
        search_models = models if models else list(self.models.keys())
        
        result_guids: Set[str] = None
        
        for model_name in search_models:
            if model_name not in self.models:
                continue
            
            model = self.models[model_name]
            model_guids: Set[str] = set()
            
            # If entity_types specified, get components of those types
            if entity_types:
                for entity_type in entity_types:
                    if entity_type in model['by_type']:
                        model_guids.update(model['by_type'][entity_type])
            else:
                # Get all component GUIDs in this model
                model_guids.update(model['by_componentGuid'].keys())
            
            # If components specified, intersect with those
            if components:
                model_guids.intersection_update(set(components))
            
            # Union with result from other models
            if result_guids is None:
                result_guids = model_guids
            else:
                result_guids.update(model_guids)
        
        # Convert component GUIDs to entity GUIDs
        entity_guids: Set[str] = set()
        
        for model_name in search_models:
            if model_name not in self.models:
                continue
            
            model = self.models[model_name]
            
            for component_guid in (result_guids or set()):
                if component_guid in model['by_componentGuid']:
                    entity_guid = model['by_componentGuid'][component_guid].get('entityGuid')
                    if entity_guid:
                        entity_guids.add(entity_guid)
        
        return sorted(list(entity_guids))
    
    def get_component_guids(self,
                           models: Optional[List[str]] = None,
                           entity_guids: Optional[List[str]] = None,
                           entity_types: Optional[List[str]] = None) -> List[str]:
        """Query for component GUIDs
        
        Args:
            models: List of model names (None = all models)
            entity_guids: List of entity GUIDs to filter by (None = all entities)
            entity_types: List of entity types to filter by (None = all types)
            
        Returns:
            List of component GUIDs matching the criteria
        """
        # Determine which models to search
        search_models = models if models else list(self.models.keys())
        
        result_guids: Set[str] = None
        
        for model_name in search_models:
            if model_name not in self.models:
                continue
            
            model = self.models[model_name]
            model_guids: Set[str] = set()
            
            # If entity_types specified, get components of those types
            if entity_types:
                for entity_type in entity_types:
                    if entity_type in model['by_type']:
                        model_guids.update(model['by_type'][entity_type])
            
            # If entity_guids specified, get components for those entities
            if entity_guids:
                entity_component_guids: Set[str] = set()
                for entity_guid in entity_guids:
                    if entity_guid in model['by_entity']:
                        entity_component_guids.update(model['by_entity'][entity_guid])
                
                if model_guids:
                    model_guids.intersection_update(entity_component_guids)
                else:
                    model_guids = entity_component_guids
            
            # If neither filter specified, get all components
            if not entity_types and not entity_guids:
                model_guids = set(model['by_componentGuid'].keys())
            
            # Union with result from other models
            if result_guids is None:
                result_guids = model_guids
            else:
                result_guids.update(model_guids)
        
        return sorted(list(result_guids or set()))
    
    def get_components(self, guids: List[str]) -> List[Dict]:
        """Retrieve component data by GUIDs
        
        Args:
            guids: List of component GUIDs to retrieve
            
        Returns:
            List of component dictionaries
        """
        components = []
        
        # Search all models for the GUIDs
        for model_name in self.models:
            model = self.models[model_name]
            
            for guid in guids:
                if guid in model['by_componentGuid']:
                    components.append(model['by_componentGuid'][guid])
        
        return components
    
    def get_models(self) -> List[str]:
        """Get list of all loaded models
        
        Returns:
            List of model names
        """
        return sorted(list(self.models.keys()))
    
    def get_entity_types(self, models: Optional[List[str]] = None) -> List[str]:
        """Get list of all entity types across models
        
        Args:
            models: List of model names (None = all models)
            
        Returns:
            List of entity types
        """
        search_models = models if models else list(self.models.keys())
        types: Set[str] = set()
        
        for model_name in search_models:
            if model_name in self.models:
                types.update(self.models[model_name]['by_type'].keys())
        
        return sorted(list(types))
