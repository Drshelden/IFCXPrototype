#!/usr/bin/env python
"""Trace full get_components query logic"""

import sys
import traceback
sys.path.insert(0, '.')
sys.path.insert(0, 'dataStores/fileBased')
sys.path.insert(0, 'utils/ifc_utils')

try:
    from server import IFCProcessingServer

    # Create server
    server = IFCProcessingServer('fileBased')

    # Simulate the query
    entity_types = ['IfcWall']
    models = ['HelloWall-01']
    entity_guids = None
    component_guids = None
    component_types = None

    print("=== Simulating /api/components?entityTypes=IfcWall&models=HelloWall-01 ===\n")

    # Step 1: Check condition
    print(f"Step 1: Check condition")
    print(f"  component_guids: {component_guids}")
    print(f"  component_types: {component_types}")
    print(f"  entity_types: {entity_types}")
    if not component_guids:  # branch 1
        print("  -> Not branch 1 (no component_guids)")
    if component_types:  # branch 2
        print("  -> Not branch 2 (no component_types)")
    if models or entity_types or entity_guids:  # branch 3
        print("  -> BRANCH 3: Using entity_types/entity_guids\n")
        
        # Step 2: Get search models
        search_models = models if models else server.memory_tree.get_models()
        print(f"Step 2: search_models = {search_models}\n")
        
        # Step 3: Expand entity types
        print(f"Step 3: Expanding entity types")
        expanded_types = server._expand_entity_types_for_models(entity_types, search_models) if entity_types else {}
        print(f"  expanded_types = {expanded_types}\n")
        
        # Step 4: Query for each model
        print(f"Step 4: Query components for each model")
        found_guids = set()
        for model_name in search_models:
            model_entity_types = None
            if entity_types:
                model_entity_types = expanded_types.get(model_name, [])
                print(f"  Model {model_name}:")
                print(f"    model_entity_types = {model_entity_types}")
                if not model_entity_types and not entity_guids:
                    print(f"    -> No types and no guids, CONTINUE")
                    continue
            
            print(f"    Calling get_component_guids...")
            model_guids = server.memory_tree.get_component_guids(
                models=[model_name],
                entity_types=model_entity_types,
                entity_guids=entity_guids
            )
            print(f"    -> Found {len(model_guids)} component GUIDs")
            found_guids.update(model_guids)
        
        print(f"\nStep 5: Total found_guids: {len(found_guids)}\n")
        
        # Step 6: Get components
        print(f"Step 6: Fetching component data")
        components = server.memory_tree.get_components(list(found_guids), models=search_models)
        print(f"  -> Found {len(components)} components\n")

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()

