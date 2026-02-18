#!/usr/bin/env python
"""Test the full query logic"""

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
    print(f"3. Model '{model_name}':")
    print(f"   Available: {sorted(model_types)}")
    print(f"   Result: {per_model[model_name]}")

# Now query with the expanded types
print(f"\n4. Querying with expanded types:")
for model_name in models:
    model_entity_types = per_model.get(model_name, [])
    print(f"   Model '{model_name}' entity_types: {model_entity_types}")
    
    entity_guids = tree.get_entity_guids(
        models=[model_name],
        entity_types=model_entity_types
    )
    print(f"   Found {len(entity_guids)} entity GUIDs: {entity_guids}")
