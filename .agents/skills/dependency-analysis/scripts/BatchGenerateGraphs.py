#!/usr/bin/env python3
"""
Batch Form Dependency Graph Generator
=====================================

Purpose:
    Reads a list of form IDs from forms-to-search.csv and generates dependency
    graphs for each form using GenerateFormDependencyGraph.py.

Input:
    - forms-to-search.csv (List of form IDs to process)
    - GenerateFormDependencyGraph.py (Individual graph generator)

Output:
    - PNG dependency graph images saved to dependency-graphs/ folder

Key Functions:
    - generate_graphs_for_forms(): Batch processes forms with specified options

Usage:
    python BatchGenerateGraphs.py                    # Default: level 1, forms only, silent
    python BatchGenerateGraphs.py -type ALL         # Include reports and forms
    python BatchGenerateGraphs.py -levels 2 -type R # 2-level report graphs
    python BatchGenerateGraphs.py --show            # Display graphs interactively

Related:
    - GenerateFormDependencyGraph.py: Single form graph generator
    - form_relationships.csv: Relationship data source
"""

import csv
import subprocess
import os
import argparse

## Default behavior (level 1, forms only, silent)
#py .\FormRelationships\BatchGenerateGraphs.py

# Show both forms and reports (either way works)
#py .\FormRelationships\BatchGenerateGraphs.py
#py .\FormRelationships\BatchGenerateGraphs.py -type ALL

# Show only forms
#py .\FormRelationships\python BatchGenerateGraphs.py -type F

# Show only reports
#py .\FormRelationships\BatchGenerateGraphs.py -type R

# Generate 2-level reports
#py .\FormRelationships\BatchGenerateGraphs.py -levels 2 -type R

# Generate forms and show the graphs
#py .\FormRelationships\BatchGenerateGraphs.py -type F --show

def generate_graphs_for_forms(levels=1, type=None, silent=True):
    """
    Reads forms from forms-to-search.csv and generates dependency graphs for each form
    using GenerateFormDependencyGraph.py with specified parameters
    
    Args:
        levels (int): Number of levels to include in the graph
        type (str): Type filter - 'F' for forms, 'R' for reports, None for both
        silent (bool): Whether to run in silent mode
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, "forms-to-search.csv")
    graph_generator = os.path.join(base_dir, "GenerateFormDependencyGraph.py")

    try:
        with open(input_csv, 'r') as file:
            csv_reader = csv.DictReader(file)
            forms = [row['form'].strip() for row in csv_reader if row['form'].strip()]
            
        print(f"Found {len(forms)} forms to process")
        print(f"Using parameters: levels={levels}, type={type}, silent={silent}")
        
        for i, form in enumerate(forms, 1):
            print(f"Processing {i}/{len(forms)}: {form}")
            
            cmd = [
                'python',
                graph_generator,
                '-form', form,
                '-levels', str(levels)
            ]
            
            # Only add type filter if specified
            if type:
                cmd.extend(['-type', type])
                
            if silent:
                cmd.append('-silent')
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Successfully generated graph for {form}")
                else:
                    print(f"Error generating graph for {form}: {result.stderr}")
            except Exception as e:
                print(f"Failed to process {form}: {str(e)}")
                
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Batch generate form dependency graphs')
    parser.add_argument('-levels', type=int, default=1,
                      help='Number of levels to include (default: 1)')
    parser.add_argument('-type', choices=['F', 'R', 'ALL'], default=None,
                      help='Filter type: F for forms, R for reports, ALL or omit for both (default: ALL)')
    parser.add_argument('--show', action='store_true',
                      help='Show graphs (turns off silent mode)')
    
    args = parser.parse_args()
    
    # Convert 'ALL' to None for no filtering
    type_filter = None if args.type == 'ALL' else args.type
    
    print("Starting batch graph generation...")
    generate_graphs_for_forms(
        levels=args.levels,
        type=type_filter,
        silent=not args.show
    )
    print("Batch processing complete!")

if __name__ == "__main__":
    main()