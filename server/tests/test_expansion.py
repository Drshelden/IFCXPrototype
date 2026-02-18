#!/usr/bin/env python
"""Test hierarchy expansion logic"""

from utils.ifc_utils.ifc_descendants_export import IFCDescendantsExporter
from dataStores.fileBased.memoryTree import MemoryTree

# Initialize
exporter = IFCDescendantsExporter()
tree = MemoryTree()
tree.refresh_from_store(r'dataStores\fileBased\data')

# Get available entity types in HelloWall-01
available_types = set(tree.get_entity_types(models=['HelloWall-01']))
print(f"Available entity types in HelloWall-01: {sorted(available_types)}")

# Get descendants of IfcWall
descendants = exporter.get_descendants('IfcWall')
print(f"Descendants of IfcWall: {descendants}")

# Check intersection
intersection = available_types.intersection(descendants)
print(f"Intersection: {intersection}")

# Also check what entities have each type
for entity_type in available_types:
    entity_guids = tree.get_entity_guids(models=['HelloWall-01'], entity_types=[entity_type])
    print(f"  {entity_type}: {len(entity_guids)} entities")
