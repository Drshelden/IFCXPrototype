#!/usr/bin/env python3
"""
Batch IFC to JSON Processor

This script processes all IFC files in the data folder and its subdirectories,
generating corresponding JSON files using the ifc4ingestor.py module.
"""

import os
import sys
import json
from pathlib import Path

# Add server directory to Python path to import the ingestor
server_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(server_dir))

from ingestors.ifc4ingestor import IFC2JSONSimple


def find_ifc_files(root_dir):
    """
    Recursively find all IFC files in the given directory.
    
    Args:
        root_dir (str or Path): Root directory to search
        
    Returns:
        list: List of Path objects for each IFC file found
    """
    root_path = Path(root_dir)
    ifc_files = []
    
    for file_path in root_path.rglob("*.ifc"):
        ifc_files.append(file_path)
    
    return sorted(ifc_files)


def process_ifc_file(ifc_path, output_path=None, compact=False, empty_properties=False):
    """
    Process a single IFC file and generate JSON output.
    
    Args:
        ifc_path (Path): Path to the IFC file
        output_path (Path): Path for the output JSON file (default: same as IFC with .json extension)
        compact (bool): If True, output compact JSON without pretty printing
        empty_properties (bool): If True, include empty properties in output
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Generate output path if not provided
        if output_path is None:
            output_path = ifc_path.with_suffix('.json')
        
        print(f"Processing: {ifc_path}")
        
        # Extract model name from parent directory
        model_name = ifc_path.parent.name
        
        # Create converter instance
        converter = IFC2JSONSimple(
            str(ifc_path),
            COMPACT=compact,
            EMPTY_PROPERTIES=empty_properties,
            modelName=model_name
        )
        
        # Convert to JSON
        json_objects = converter.spf2Json()
        
        # Write to output file
        with open(output_path, 'w') as f:
            json.dump(json_objects, f, indent=None if compact else 2, default=str)
        
        print(f"  ✓ Generated: {output_path} ({len(json_objects)} entities)")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {ifc_path}: {e}")
        return False


def main():
    """Main function to process all IFC files in the data directory."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process all IFC files in the data folder and generate JSON files'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Root data directory containing IFC files (default: data)'
    )
    parser.add_argument(
        '--compact',
        action='store_true',
        help='Generate compact JSON without pretty printing'
    )
    parser.add_argument(
        '--empty-properties',
        action='store_true',
        help='Include empty properties in output'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show which files would be processed without actually processing them'
    )
    
    args = parser.parse_args()
    
    # Resolve data directory path (relative to project root)
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / args.data_dir
    
    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' does not exist.")
        sys.exit(1)
    
    # Find all IFC files
    print(f"Searching for IFC files in: {data_dir}")
    print("-" * 70)
    
    ifc_files = find_ifc_files(data_dir)
    
    if not ifc_files:
        print("No IFC files found.")
        sys.exit(0)
    
    print(f"Found {len(ifc_files)} IFC file(s):\n")
    for ifc_file in ifc_files:
        print(f"  • {ifc_file.relative_to(project_root)}")
    
    print("\n" + "=" * 70)
    
    if args.dry_run:
        print("Dry run mode - no files will be processed.")
        sys.exit(0)
    
    # Process each IFC file
    print(f"Processing IFC files...\n")
    
    success_count = 0
    failure_count = 0
    
    for ifc_file in ifc_files:
        if process_ifc_file(ifc_file, compact=args.compact, empty_properties=args.empty_properties):
            success_count += 1
        else:
            failure_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Processing complete!")
    print(f"  Successfully processed: {success_count}")
    print(f"  Failed: {failure_count}")
    print(f"  Total: {len(ifc_files)}")


if __name__ == '__main__':
    main()
