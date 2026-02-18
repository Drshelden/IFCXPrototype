#!/usr/bin/env python
"""Test entityTypes query via API"""

import requests

base_url = "http://localhost:5000"

# Test 1: Concrete type that should work
print("Test 1: Concrete entity type (IfcWallStandardCase)")
r = requests.get(f"{base_url}/api/components?entityTypes=IfcWallStandardCase&models=HelloWall-01")
data = r.json()
print(f"  Result: {len(data)} models, {sum(len(v) for v in data.values())} components")
print(f"  Models: {list(data.keys())}")

# Test 2: Parent type (should expand to subtype)
print("\nTest 2: Parent entity type (IfcWall) - expecting expansion to subtypes")
r = requests.get(f"{base_url}/api/components?entityTypes=IfcWall&models=HelloWall-01")
data = r.json()
print(f"  Result: {len(data)} models, {sum(len(v) for v in data.values())} components")
print(f"  Models: {list(data.keys())}")
if 'HelloWall-01' in data:
    print(f"  Components: {[c.get('componentType', 'unknown') for c in data['HelloWall-01'][:3]]}")

# Test 3: Query entity types directly to see what's available
print("\nTest 3: Available entity types in HelloWall-01")
r = requests.get(f"{base_url}/api/entityTypes?models=HelloWall-01")
types = r.json()
wall_types = [t for t in types if 'Wall' in t]
print(f"  Available Wall types: {wall_types}")
