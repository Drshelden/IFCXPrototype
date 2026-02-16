  # IFCJSON_python - ifc2json_simple.py
# Simplified IFC to JSON converter - prints first-level attributes
# https://github.com/IFCJSON-Team

# MIT License

from datetime import datetime
import hashlib
import uuid
import json
import sys
import argparse
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid as guid
from utils import toLowerCamelcase, generateDeterministicGuid, expandGuid

INCLUDE_EMPTY_PROPERTIES = False


ALLOWED_TYPES = {'IfcObjectDefinition', 'IfcPropertySet', 'IfcRelationship'}
# ALLOWED_TYPES = {'IfcObjectDefinition', 'IfcPropertySet'}


# Define attributes to exclude
EXCLUDE_ATTRIBUTES = {
    'ownerhistory',
    'id',
    'step_id',
    'objectplacement',
    'representation',
    'representations',
    'representationmaps',
    'representationcontexts',
    'unitsincontext'
}

# Define attribute name substitutions
ATTRIBUTE_SUBSTITUTIONS = {
    'GlobalId': 'entityGuid',
    'Name': 'componentName',
    'Description': 'componentDescription',
    'HasPropertySets': 'propertySets',
    'type': 'componentType'
}

EXPAND_GUID_ATTRIBUTES = {'GlobalId'}

class IFC2JSONSimple:
    """Simplified IFC to JSON converter that prints entity attributes"""
    
    SCHEMA_VERSION = '0.0.1'

    settings = ifcopenshell.geom.settings()
    # settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)
    settings.set("use-world-coords", True)

    def __init__(self, ifcModel, COMPACT=False, EMPTY_PROPERTIES=False):
        """IFC SPF simplified converter

        parameters:
        ifcModel: IFC filePath or ifcopenshell model instance
        COMPACT (boolean): if True then pretty print is turned off
        """
        if isinstance(ifcModel, ifcopenshell.file):
            self.ifcModel = ifcModel
        else:
            self.ifcModel = ifcopenshell.open(ifcModel)
        self.COMPACT = COMPACT
        self.EMPTY_PROPERTIES = EMPTY_PROPERTIES

        # Dictionary referencing all objects with a GlobalId that are already created
        self.rootObjects = {}

        # Dictionary referencing all objects with a GlobalId that are already created
        self.includeObjects = {}

        # Representations are kept seperate to be added to the end of the list
        self.representations = []



    # def createReferenceObject(self, entityAttributes, COMPACT=False):
    #     """Returns object reference

    #     Parameters:
    #     entityAttributes (dict): Dictionary of IFC object data
    #     COMPACT (boolean): verbose or non verbose IFC.JSON-5a output

    #     Returns:
    #     dict: object containing reference to another object

    #     """
    #     ref = {}
    #     if not COMPACT:

    #         # Entity names must be stripped of Ifc prefix
    #         ref['type'] = entityAttributes['type'][3:]
    #     ref['ref'] = expandGuid(entityAttributes['GlobalId']) if 'GlobalId' in entityAttributes else None
    #     return ref

    def spf2Json(self):
        """
        Iterate through all entities in the IFC file and print their first-level attributes

        Returns:
        list: List of dictionaries containing entity attributes
        """        


        jsonObjects = []

        for entity in self.ifcModel:
            if hasattr(entity, 'GlobalId') and entity.GlobalId:
                self.rootObjects[entity.id()] = guid.split(
                    guid.expand(entity.GlobalId))[1:-1]
            # else:
            #     print(f"Warning: Entity of type {entity.is_a()} with id {entity.id()} does not have a GlobalId and will not be referenced.")
        
        # Create a list of entities by querying for each allowed type
        entity_list = []
        # for allowed_type in reversed(list(ALLOWED_TYPES)):
        for allowed_type in ALLOWED_TYPES:
            entities_of_type = self.ifcModel.by_type(allowed_type)
            entity_list.extend(entities_of_type)
        
        # Iterate through all queried entities

        for entity in entity_list:
            returnedValue = self.processEntry(entity, topLevel=True)
            if returnedValue is not None:   
                jsonObjects.append(returnedValue)

        jsonObjects = jsonObjects + list(self.representations)
        return jsonObjects
    
    def processEntry(self, entity, topLevel=False):
        # Get entity type
        if not topLevel and hasattr(entity, 'GlobalId') and entity.GlobalId:
            entityGuid = expandGuid(entity.GlobalId)
            return entityGuid
        
        entity_type = entity.is_a()
        
        entity_dict = {}
        

        
        # Get all first-level attributes from __dict__
        entityAttributes = entity.__dict__

        if hasattr(entity, 'GlobalId') and entity.GlobalId: fc = True
        else: fc = False

        if(entity.is_a('IfcObjectDefinition')):
            isEntityDefinition = True
        else:            
            isEntityDefinition = False

        if 'Representation' in entityAttributes:
                obj = self.toObj(entity)

                if obj:
                    # id = guid.split(guid.expand(guid.new()))[1:-1]
                    # ref = {}
                    # if not self.COMPACT:
                    #     ref['type'] = "shapeRepresentation"
                    # ref['ref'] = id
                    # entityAttributes['representations'] = [ref]
                    entityGuid = expandGuid(entity.GlobalId)
                    componentGuid = generateDeterministicGuid("ShapeRepresentationComponent", entityGuid)    
                    self.representations.append(
                        {
                            "componentGuid": componentGuid,
                            "componentType": "IfcShapeRepresentationComponent",
                            "entityGuid": entityGuid,
                            "representationIdentifier": "Body",
                            "representationFormat": "OBJ",
                            "items": [
                                obj
                            ]
                        }
                    )

                # # (!) delete original representation, even if OBJ generation fails
                # del entityAttributes['Representation']

        returnedAttributes = self.appendAttributes(entityAttributes, entity_type, fc, isEntityDefinition)
        entity_dict.update(returnedAttributes)
        
        # Sort entity_dict alphabetically by keys
        entity_dict = dict(sorted(entity_dict.items()))

        return entity_dict

    def appendAttributes(self, entityAttributes, entity_type, isFirstClass=False, isEntityDefinition=False):

        entity_dict = {}        
        
        if isFirstClass:
            # Extract component type for GUID generation and output
            componentType = entity_type + 'Component'
            entity_dict['componentType'] = componentType
        
        if isEntityDefinition:
            entity_dict['entityType'] = entity_type         

        keys = sorted(entityAttributes.keys())  
            
        for attr_name in keys:
            # Skip excluded attributes
            if attr_name.lower() in EXCLUDE_ATTRIBUTES:
                continue

            # Skip internal attributes
            if attr_name.startswith('_'):
                continue
            
            attr_value = entityAttributes[attr_name]
                            
            # Convert to JSON-serializable format using getAttributeValue
            try:
                json_value = self.getAttributeValueNew(attr_value)
            except:
                json_value = None
            
            # If this is GlobalId (converted to entityGuid), expand it to standard UUID format
            if attr_name in EXPAND_GUID_ATTRIBUTES and json_value is not None:
                json_value = expandGuid(json_value)

            
            # If this is the type attribute being converted to componentType, append "Component"
            if attr_name == 'type' and json_value is not None:
                json_value = json_value + 'Component'
            
            # Print attribute name and type
            attr_type = type(attr_value).__name__

            # Apply substitution to attribute name if it exists in ATTRIBUTE_SUBSTITUTIONS
            if isFirstClass and attr_name in ATTRIBUTE_SUBSTITUTIONS:
                display_attr_name = ATTRIBUTE_SUBSTITUTIONS[attr_name]
            else:
                display_attr_name = attr_name
                            
            # Convert to camelCase
            display_attr_name = toLowerCamelcase(display_attr_name)
            
            # Only add to dict if there's a value or if empty properties should be included
            # Skip if this key already exists in entity_dict (to avoid overwriting manually set values)
            if display_attr_name not in entity_dict:
                if json_value is not None:
                    entity_dict[display_attr_name] = json_value
                elif INCLUDE_EMPTY_PROPERTIES:
                    entity_dict[display_attr_name] = ""
        
        # Generate deterministic GUID and place it as the first attribute
        if 'componentType' in entity_dict and 'entityGuid' in entity_dict:
            deterministic_guid = generateDeterministicGuid(
                entity_dict['componentType'],
                entity_dict['entityGuid']
            )
            # Create new dict with componentGuid first, then all existing entries
            ordered_dict = {'componentGuid': deterministic_guid}
            ordered_dict.update(entity_dict)
            entity_dict = ordered_dict

        return entity_dict

    def getAttributeValueNew(self, value):
        """Helper function to convert attribute values to JSON-serializable format"""
        if value is None:
            return None
        elif isinstance(value, ifcopenshell.entity_instance):
            return self.processEntry(value)
            # Check if this is an IfcObject that should be processed
            # if value.is_a('IfcObject'):
            #     return self.processEntry(value)
            # else:
            #     return self.createReferenceObject(value.__dict__, self.COMPACT)
        elif isinstance(value, tuple):
            return tuple(self.getAttributeValueNew(v) for v in value)
        else:
            return value
        
    def toObj(self, entity):
        """Convert IfcProduct to OBJ mesh

        parameters:
        entity: ifcopenshell ifcProduct instance

        Returns:
        string: OBJ string
        """

        if entity.Representation:
            try:
                shape = ifcopenshell.geom.create_shape(self.settings, entity)

                # Check if geometry has verts and faces attributes
                if not hasattr(shape.geometry, 'verts') or not hasattr(shape.geometry, 'faces'):
                    return None

                verts = shape.geometry.verts
                vertsList = [' '.join(map(str, verts[x:x+3]))
                             for x in range(0, len(verts), 3)]
                vertString = 'v ' + '\nv '.join(vertsList) + '\n'

                faces = shape.geometry.faces
                facesList = [' '.join(map(str, [f + 1 for f in faces[x:x+3]]))
                             for x in range(0, len(faces), 3)]
                faceString = 'f ' + '\nf '.join(map(str, facesList)) + '\n'

                return vertString + faceString
            except Exception as e:
                print(str(e) + ': Unable to generate OBJ data for ' +
                      str(entity))
                return None





def main():
    """Main entry point for processing IFC files"""
    parser = argparse.ArgumentParser(
        description='Convert IFC file to JSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ifc4ingestor.py input.ifc
  python ifc4ingestor.py input.ifc -o output.json
  python ifc4ingestor.py input.ifc --compact
        """
    )
    
    parser.add_argument('input',
                        help='Input IFC file path')
    parser.add_argument('-o', '--output',
                        help='Output JSON file path (if not specified, prints to stdout)')
    parser.add_argument('--compact',
                        action='store_true',
                        help='Compact output (no pretty printing)')
    parser.add_argument('--empty-properties',
                        action='store_true',
                        help='Include empty properties in output')
    
    args = parser.parse_args()


    
    # Check if input file exists
    import os
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create converter instance
        converter = IFC2JSONSimple(
            args.input,
            COMPACT=args.compact,
            EMPTY_PROPERTIES=args.empty_properties
        )
        
        # Convert to JSON
        json_objects = converter.spf2Json()
        
        # Prepare output
        output_data = json_objects
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=None if args.compact else 2, default=str)
            print(f"Successfully wrote {len(json_objects)} entities to {args.output}")
        else:
            json_output = json.dumps(output_data, indent=None if args.compact else 2, default=str)
            print(json_output)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()