#!/usr/bin/env python
"""Direct test of expansion logic"""

import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'dataStores/fileBased')
sys.path.insert(0, 'utils/ifc_utils')

from memoryTree import MemoryTree
from ifc_descendants_export import IFCDescendantsExporter

# Initialize
tree = MemoryTree()
tree.refresh_from_store(r'dataStores\fileBased\data')
exporter = IFCDescendantsExporter()

# Simulate the expansion logic from _expand_entity_types_for_models
entity_types = ['IfcWall']
models = ['HelloWall-01']

print("Tracing expansion logic...")
print(f"1. Input: entity_types={entity_types}, models={models}")

# Step 1: Get descendants
descendants = set()
for entity_type in entity_types:
    entity_descendants = exporter.get_descendants(entity_type)
    print(f"2. {entity_type} descendants: {entity_descendants}")
    descendants.update(entity_descendants)

# Step 2: Per-model intersection
print(f"3. All descendants collected: {descendants}")
per_model = {}
for model_name in models:
    model_types = set(tree.get_entity_types(models=[model_name]))
    print(f"4. Model {model_name} available types: {sorted(model_types)}")
    
    intersection = model_types.intersection(descendants)
    print(f"5. Intersection with descendants: {intersection}")
    per_model[model_name] = sorted(list(intersection))

print(f"\n6. Final result: {per_model}")
