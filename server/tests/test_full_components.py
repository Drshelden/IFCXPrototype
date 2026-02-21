#!/usr/bin/env python
"""Test the full component query logic"""

from utils.ifc_utils.ifc_descendants_export import IFCDescendantsExporter
from dataStores.fileBased.memoryTree import MemoryTree

# Initialize
exporter = IFCDescendantsExporter()
tree = MemoryTree()
tree.refresh_from_store(r'dataStores\fileBased\data')

# Simulate what the server does
entity_types = ['IfcWall']
models = ['HelloWall-01']

# Expand entity types for models
descendants = set()
for entity_type in entity_types:
    descendants.update(exporter.get_descendants(entity_type))

print(f"1. Input entity_types: {entity_types}")
print(f"2. Expanded descendants: {sorted(descendants)}")

# Per-model intersection (from _expand_entity_types_for_models)
per_model = {}
for model_name in models:
    model_types = set(tree.get_entity_types(models=[model_name]))
    intersection = model_types.intersection(descendants)
    per_model[model_name] = sorted(list(intersection))
    print(f"3. Model '{model_name}': {per_model[model_name]}")

# Get entity guids and then components
found_guids = set()
for model_name in models:
    model_entity_types = per_model.get(model_name, [])
    
    entity_guids = tree.get_entity_guids(
        models=[model_name],
        entity_types=model_entity_types
    )
    print(f"\n4. Model '{model_name}' entity_guids: {entity_guids}")
    
    # Need to get component guids from entity guids
    component_guids = tree.get_component_guids(
        models=[model_name],
        entity_guids=entity_guids
    )
    print(f"5. Model '{model_name}' component_guids: {len(component_guids)} found")
    found_guids.update(component_guids)

print(f"\n6. Total component_guids: {len(found_guids)}")

# Get components
components, guid_to_model = tree.get_components(list(found_guids), models=models)
print(f"7. Total components: {len(components)}")
for c in components:
    print(f"   - {c.get('componentType', 'unknown')}: {c.get('componentGuid', 'no-guid')[:8]}...")
