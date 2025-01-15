#!/usr/bin/env python3
import json
import sys
import argparse
import os
from typing import List, Dict, Any, Set

def read_objects_from_file(file_path: str) -> List[str]:
    """
    Read objects from a newline-separated file.
    
    Args:
        file_path: Path to the file containing object names
        
    Returns:
        List of object names from the file
    """
    try:
        with open(file_path, 'r') as f:
            # Read lines and strip whitespace, filter out empty lines
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        # If file doesn't exist, assume it's a direct object name
        return [file_path]
    except Exception as e:
        print(f"Error reading objects file: {str(e)}")
        sys.exit(1)

def parse_keep_argument(keep_args: List[str]) -> List[str]:
    """
    Parse the keep argument which can be either a file or direct object names.
    
    Args:
        keep_args: List of arguments from the --keep option
        
    Returns:
        List of object names to keep
    """
    objects_to_keep = []
    for arg in keep_args:
        # If the argument is a file that exists, read objects from it
        if os.path.isfile(arg):
            objects_to_keep.extend(read_objects_from_file(arg))
        else:
            # Otherwise treat it as a direct object name
            objects_to_keep.append(arg)
    return objects_to_keep

def has_sobject_reference(schema: Dict[str, Any]) -> bool:
    """Check if a schema has an allOf reference to SObject."""
    if 'allOf' in schema:
        for item in schema['allOf']:
            if '$ref' in item and 'SObject' in item['$ref']:
                return True
    return False

def get_removed_schemas(original_schemas: Dict[str, Any], filtered_schemas: Dict[str, Any]) -> Set[str]:
    """Get the set of schema names that were removed during filtering."""
    return set(original_schemas.keys()) - set(filtered_schemas.keys())

def update_sobject_type_enum(spec: Dict[str, Any], removed_schemas: Set[str]) -> None:
    """
    Update the SObjectType enum by removing values corresponding to removed schemas.
    
    Args:
        spec: The OAS specification containing the components
        removed_schemas: Set of schema names that were removed during filtering
    """
    schemas = spec['components']['schemas']
    if 'SObjectType' in schemas and 'enum' in schemas['SObjectType']:
        # Filter out enum values that correspond to removed schemas
        original_enum = schemas['SObjectType']['enum']
        filtered_enum = [
            enum_value for enum_value in original_enum
            if enum_value not in removed_schemas
        ]
        schemas['SObjectType']['enum'] = filtered_enum

def filter_components(spec: Dict[str, Any], objects_to_keep: List[str]) -> Dict[str, Any]:
    """
    Filter the components section of an OAS spec.
    
    Args:
        spec: The complete OAS specification as a dictionary
        objects_to_keep: List of object names to preserve
        
    Returns:
        Modified OAS specification with filtered components
    """
    if 'components' not in spec or 'schemas' not in spec['components']:
        return spec
    
    # Create a new schemas dictionary with only the objects we want to keep
    filtered_schemas = {}
    original_schemas = spec['components']['schemas']
    
    # First, add all objects that are in our keep list
    for obj_name in objects_to_keep:
        if obj_name in original_schemas:
            filtered_schemas[obj_name] = original_schemas[obj_name]
    
    # Then, add any objects that don't have an SObject reference
    for name, schema in original_schemas.items():
        if name not in filtered_schemas and not has_sobject_reference(schema):
            filtered_schemas[name] = schema
    
    # Get the set of removed schemas
    removed_schemas = get_removed_schemas(original_schemas, filtered_schemas)
    
    # Update the specification with filtered schemas
    spec['components']['schemas'] = filtered_schemas
    
    # Update the SObjectType enum if it exists
    update_sobject_type_enum(spec, removed_schemas)
    
    return spec

def main():
    parser = argparse.ArgumentParser(description='Filter OAS specification components')
    parser.add_argument('input_file', help='Input OAS specification JSON file')
    parser.add_argument('output_file', help='Output file for filtered specification')
    parser.add_argument('--keep', nargs='+', 
                       help='List of object names to keep or path to file containing newline-separated object names',
                       default=[])
    
    args = parser.parse_args()
    
    try:
        # Parse the keep argument
        objects_to_keep = parse_keep_argument(args.keep)
        
        # Read the input specification
        with open(args.input_file, 'r') as f:
            spec = json.load(f)
        
        # Filter the components
        filtered_spec = filter_components(spec, objects_to_keep)
        
        # Write the filtered specification
        with open(args.output_file, 'w') as f:
            json.dump(filtered_spec, f, indent=2)
            
        print(f"Successfully filtered specification. Output written to {args.output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {args.input_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file {args.input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
