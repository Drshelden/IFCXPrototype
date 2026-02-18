#!/usr/bin/env python
"""Direct test of the server's expansion method"""

import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'dataStores/fileBased')
sys.path.insert(0, 'utils/ifc_utils')

from server import IFCProcessingServer

# Create server
server = IFCProcessingServer('fileBased')

# Test the expansion method directly
entity_types = ['IfcWall']
models = ['HelloWall-01']

print("Testing server._expand_entity_types_for_models directly:")
result = server._expand_entity_types_for_models(entity_types, models)
print(f"Result: {result}")
