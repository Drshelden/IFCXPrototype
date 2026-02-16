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
import ifcopenshell.guid as guid

includeEmptyProperties = True

def convertGuid(entityGuid):
    expanded = guid.expand(entityGuid)
    # Format as UUID with dashes: 8-4-4-4-12
    return str(uuid.UUID(expanded))

def toLowerCamelcase(string):
    """Convert string from upper to lower camelCase"""
    return string[0].lower() + string[1:]

ALLOWED_TYPES = {'IfcPropertySet'}

class IFC2JSONSimple:
    """Simplified IFC to JSON converter that prints entity attributes"""
    
    SCHEMA_VERSION = '0.0.1'

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

        # Representations are kept seperate to be added to the end of the list
        self.representations = {}



    def createFullObject(self, entityAttributes):
        """Create a full nested object from entity attributes
        
        Parameters:
        entityAttributes (dict): Dictionary of IFC object data
        
        Returns:
        dict: Full object representation
        """
        return entityAttributes

    def createReferenceObject(self, entityAttributes, COMPACT=False):
        """Returns object reference

        Parameters:
        entityAttributes (dict): Dictionary of IFC object data
        COMPACT (boolean): verbose or non verbose IFC.JSON-5a output

        Returns:
        dict: object containing reference to another object

        """
        ref = {}
        if not COMPACT:

            # Entity names must be stripped of Ifc prefix
            ref['type'] = entityAttributes['type'][3:]
        ref['ref'] = convertGuid(entityAttributes['GlobalId']) if 'GlobalId' in entityAttributes else None
        return ref

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
            else:
                print(f"Warning: Entity of type {entity.is_a()} with id {entity.id()} does not have a GlobalId and will not be referenced.")
        
        # Define allowed base types to process

        #ALLOWED_TYPES = {'IfcObjectDefinition'}
        # Iterate through all entities in the IFC file
        for entity in self.ifcModel:
            # Get entity type
            entity_type = entity.is_a()
            
            # Filter: only process if entity is a subclass of allowed types
            is_allowed = False
            for allowed_type in ALLOWED_TYPES:
                if entity.is_a(allowed_type):
                    is_allowed = True
                    break
            
            if not is_allowed:
                continue
            
            entity_dict = {}
            
            # Extract component type for GUID generation and output
            componentType = entity_type + 'Component'
            entity_dict['componentType'] = componentType
            
            # Get all first-level attributes from __dict__
            entityAttributes = entity.__dict__
            
            # Define attributes to exclude
            EXCLUDE_ATTRIBUTES = {
                'OwnerHistory',
                'id',
                'step_id'
            }

            
            # Define attribute name substitutions
            ATTRIBUTE_SUBSTITUTIONS = {
                'GlobalId': 'entityGuid',
                'Name': 'componentName',
                'Description': 'componentDescription',
                'type': 'componentType'
            }
            
            # print(f"\n{'='*80}")
            # print(f"Entity Type: {entity_type}")
            # print(f"{'='*80}")

            keys = sorted(entityAttributes.keys())  
            
            for attr_name in keys:
                # Skip excluded attributes
                if attr_name in EXCLUDE_ATTRIBUTES:
                    continue
                
                attr_value = entityAttributes[attr_name]
                
                # Apply substitution and apply the substituted name for output
                display_attr_name = ATTRIBUTE_SUBSTITUTIONS.get(attr_name, attr_name)
                
                # Skip internal attributes
                if attr_name.startswith('_'):
                    continue
                
                # Convert to JSON-serializable format using getAttributeValue
                try:
                    json_value = self.getAttributeValue(attr_name, attr_value, True)
                except:
                    json_value = None
                
                # If this is GlobalId (converted to entityGuid), expand it to standard UUID format
                if attr_name == 'GlobalId' and json_value is not None:
                    try:
                        json_value = convertGuid(json_value)
                    except:
                        pass  # Keep original if expand fails
                
                # If this is the type attribute being converted to componentType, append "Component"
                if attr_name == 'type' and json_value is not None:
                    json_value = json_value + 'Component'
                
                # Print attribute name and type
                attr_type = type(attr_value).__name__
                               
                # Only add to dict if it's not None (use display_attr_name as the key)
                display_attr_name = toLowerCamelcase(display_attr_name)
                if json_value is not None:

                    entity_dict[display_attr_name] = json_value
                else:
                    if includeEmptyProperties:
                        entity_dict[display_attr_name] = ""
            
            # Generate deterministic GUID and place it as the first attribute
            if 'componentType' in entity_dict and 'entityGuid' in entity_dict:
                deterministic_guid = self.generateDeterministicGuid(
                    entity_dict['componentType'],
                    entity_dict['entityGuid']
                )
                # Create new dict with guid first, then all existing entries
                orderedObject = {'guid': deterministic_guid}
                orderedObject.update(entity_dict)
                jsonObjects.append(orderedObject)
            else:
                jsonObjects.append(entity_dict)

        return jsonObjects

    def generateDeterministicGuid(self, componentType, entityGuid):
        """Generate a deterministic GUID based on component type and entity GUID
        
        Parameters:
        componentType (str): The component type string
        entityGuid (str): The entity GUID
        
        Returns:
        str: A GUID formatted as 01695e4-f7c6-46b0-8f70-8a0172df5a1
        """
        # Create a hash from the combination of componentType and entityGuid
        hash_input = f"{componentType}:{entityGuid}".encode('utf-8')
        hash_obj = hashlib.sha256(hash_input)
        hash_hex = hash_obj.hexdigest()
        
        # Create a UUID from the hash (using namespace and name approach)
        guid_obj = uuid.UUID(bytes=hash_obj.digest()[:16])
        guid_str = str(guid_obj)
        
        # Format as the required format (removing dashes and re-adding in specific positions)
        guid_clean = guid_str.replace('-', '')
        formatted_guid = f"{guid_clean[0:8]}-{guid_clean[8:12]}-{guid_clean[12:16]}-{guid_clean[16:20]}-{guid_clean[20:32]}"
        
        return formatted_guid

    def getAttributeValue(self, key_name, value, isRoot=False):
        """Recursive method that walks through all nested objects of an attribute
        and returns a IFC.JSON-4 model structure

        Parameters:
        key_name (str): The name of the attribute being processed
        value: The value of the attribute being processed

        Returns:
        attribute data converted to IFC.JSON-4 model structure
        """
        if value == None or value == '':
            jsonValue = None

        elif isinstance(value, ifcopenshell.entity_instance):
            entity = value
            entityAttributes = entity.__dict__

            if not isRoot:
                # If not root, do not process nested objects
                return convertGuid(entityAttributes['GlobalId']) if 'GlobalId' in entityAttributes else None

            # Handle entity references
            if entity.is_a('IfcPropertySet'):
                if isinstance(value, tuple):
                    jsonValue = tuple(x for x in map(
                    lambda v: self.getAttributeValue(key_name, v, False), value) if x is not None)
                    return jsonValue
                return self.createReferenceObject(entityAttributes, self.COMPACT)

            # Handle wrapped values
            if entity.is_a('IfcInteger') or entity.is_a('IfcReal') or entity.is_a('IfcBoolean') or entity.is_a('IfcLabel') or entity.is_a('IfcText'):
                return value.wrappedValue

            # All objects with a GlobalId must be referenced
            entity_id = entity.id()
            if self.rootObjects and entity_id in self.rootObjects:
                entityAttributes["GlobalId"] = self.rootObjects[entity.id()]
                return self.createReferenceObject(entityAttributes, self.COMPACT)
            else:
                if 'GlobalId' in entityAttributes:
                    entityAttributes["GlobalId"] = guid.split(
                        guid.expand(entity.GlobalId))[1:-1]

            return self.createFullObject(entityAttributes)
        elif isinstance(value, tuple):
            jsonValue = tuple(x for x in map(
                lambda v: self.getAttributeValue(key_name, v, False), value) if x is not None)
        else:
            jsonValue = value
        return jsonValue


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
        output_data = {
            'version': converter.SCHEMA_VERSION,
            'timestamp': datetime.now().isoformat(),
            'entities': json_objects
        }
        
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