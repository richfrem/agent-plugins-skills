#!/usr/bin/env python3
"""
Form Dependency Graph Generator
===============================

Purpose:
    Generates a visual dependency graph (PNG image) for a specified Oracle Form,
    showing parent-child relationships up to N levels deep.

Input:
    - form_relationships.csv (Parent/Child relationship data)
    - Command-line arguments for form ID, levels, and filter type

Output:
    - PNG image saved to dependency-graphs/{FORM_ID}_LEVELS_{N}_TYPE_{T}.png

Key Functions:
    - read_relationships(): Parses CSV for parent-child edges
    - build_graph(): Constructs NetworkX directed graph
    - get_descendants_limited(): BFS traversal to specified depth
    - plot_graph(): Renders graph with matplotlib using shell layout

Usage:
    python GenerateFormDependencyGraph.py -form FORM0000           # All levels
    python GenerateFormDependencyGraph.py -form FORM0000 -levels 2 # 2 levels
    python GenerateFormDependencyGraph.py -form FORM0000 -type F   # Forms only
    python GenerateFormDependencyGraph.py -form FORM0000 -type R   # Reports only

Related:
    - BatchGenerateGraphs.py: Batch processor for multiple forms
    - dependencies.py: Alternative text-based trace tool
"""
import csv
import sys
import os
import argparse
import json
import re
import networkx as nx
import matplotlib.pyplot as plt

# Paths
CWD = os.getcwd()
REF_DATA_DIR = os.path.join(CWD, 'legacy-system', 'reference-data')
MASTER_COLLECTION_PATH = os.path.join(REF_DATA_DIR, 'master_object_collection.json')

# Load the Master Collection for type resolution
MASTER_COLLECTION = {}
if os.path.exists(MASTER_COLLECTION_PATH):
    try:
        with open(MASTER_COLLECTION_PATH, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            MASTER_COLLECTION = full_data.get('objects', full_data)
        print(f"Loaded {len(MASTER_COLLECTION)} objects from Master Collection for type resolution.")
    except Exception as e:
        print(f"Warning: Could not load Master Collection: {e}")

def resolve_type(node_id):
    """
    Resolves the object type using the Master Collection.
    Fallback to naming heuristics if not found.
    """
    if not isinstance(node_id, str):
        return 'UNKNOWN'
        
    name_upper = node_id.upper()
    
    # 1. Direct Lookup
    if name_upper in MASTER_COLLECTION:
        return MASTER_COLLECTION[name_upper].get('type', 'UNKNOWN').upper()
    
    # 2. Key-based Heuristic (Handling common suffixes)
    base_name = re.sub(r'_(FMB|MMB|PLL|XML|RDF|TXT|PLD)$', '', name_upper)
    if base_name in MASTER_COLLECTION:
        return MASTER_COLLECTION[base_name].get('type', 'UNKNOWN').upper()

    # 3. Pattern-based Fallback
    if re.match(r'^[A-Z]{3,4}R\d+', name_upper) or name_upper.startswith('RFL'):
        return 'REPORT'
    if re.match(r'^[A-Z]{3,4}[FME]\d+', name_upper):
        return 'FORM'
        
    return 'UNKNOWN'

def is_report(node_id):
    """Checks if a node ID corresponds to a report."""
    return resolve_type(node_id) == 'REPORT'

def read_relationships(csv_path):
    """Read parent-child relationships from CSV and return as a list of tuples."""
    relationships = []
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            # Support both legacy PARENT/CHILD and new Source/Target headers
            headers = [h.upper() for h in reader.fieldnames]
            p_col = 'PARENT' if 'PARENT' in headers else 'SOURCE' if 'SOURCE' in headers else None
            c_col = 'CHILD' if 'CHILD' in headers else 'TARGET' if 'TARGET' in headers else None
            
            if not p_col or not c_col:
                print(f"Error: CSV file '{csv_path}' must contain (PARENT/CHILD) or (Source/Target) columns.")
                sys.exit(1)
            
            for row in reader:
                # Find the actual case-sensitive header name
                h_p = [h for h in reader.fieldnames if h.upper() == p_col][0]
                h_c = [h for h in reader.fieldnames if h.upper() == c_col][0]
                
                if not row[h_p] or not row[h_c]:
                    continue
                parent = row[h_p].strip().upper()
                child = row[h_c].strip().upper()
                relationships.append((parent, child))
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    return relationships

def build_graph(relationships):
    """Build a directed graph from parent-child relationships."""
    G = nx.DiGraph()
    G.add_edges_from(relationships)
    return G

def get_descendants_limited(G, root, levels):
    """
    Return a subgraph containing root and direct descendants up to given levels
    within the filtered graph G, and a dictionary mapping nodes to their level
    from the root.
    """
    subG = nx.DiGraph()
    node_levels = {} # Dictionary to store node levels relative to the root

    # If the root node doesn't exist in the original graph G (which is already filtered),
    # return empty subgraph and dict.
    if root not in G.nodes():
        return subG, node_levels

    # Always include the root node and set its level to 0
    subG.add_node(root)
    node_levels[root] = 0

    # If levels is 0, return only the root node and its level
    if levels == 0:
        return subG, node_levels

    # Logic for levels > 0 (BFS traversal)
    edges_to_add = set() # Use a set to avoid duplicate edges
    current_frontier = {root} # Nodes at the current level being processed

    # Perform BFS level by level
    for current_level_num in range(levels):
        next_frontier = set() # Nodes for the next level
        for node in current_frontier:
            # Get direct children for the current node from the graph G (which is already filtered)
            children = list(G.successors(node))
            for child in children:
                 # Add edge from current node to child
                 edges_to_add.add((node, child))

                 # Set level for the child if not already set
                 # The level is one more than the parent's level
                 if child not in node_levels:
                     node_levels[child] = current_level_num + 1
                     next_frontier.add(child) # Add child to the next level's frontier

        # If no new nodes were found at the next level, stop
        if not next_frontier:
            break

        # Move to the next level
        current_frontier = next_frontier

    # Add all nodes that were assigned a level (including the root)
    subG.add_nodes_from(node_levels.keys())
    # Add all edges found within the specified levels
    subG.add_edges_from(list(edges_to_add))

    # Ensure the root is in the subgraph even if it has no descendants within levels > 0
    if root not in subG.nodes() and root in G.nodes():
         subG.add_node(root)
         node_levels[root] = 0 # Ensure level is set

    return subG, node_levels


def get_descendants_subgraph(G, root):
    """
    Return the subgraph containing root and all its descendants *within the filtered graph G*,
    and a dictionary mapping nodes to their shortest path level from the root.
    """
    # Ensure the root node exists in the graph G (which is already filtered)
    if root not in G.nodes():
        return nx.DiGraph(), {} # Return empty graph and dict

    # Get all descendants from the filtered graph G
    descendants = nx.descendants(G, root)
    nodes_to_include = list(descendants)
    nodes_to_include.append(root) # Add the root itself

    # Create the subgraph from the filtered graph G
    subG = G.subgraph(nodes_to_include).copy()

    # Calculate shortest path levels for all nodes in the subgraph from the root
    try:
        node_levels = nx.shortest_path_length(subG, source=root)
    except nx.NetworkXNoPath:
         # If the root is isolated or some nodes are unreachable in the subgraph (shouldn't happen with descendants)
         node_levels = {root: 0}
         print(f"Warning: Could not calculate shortest paths from root '{root}' for all nodes in subgraph.")
         # For nodes in subG that are not in shortest_path_length, assign a level (e.g., -1)
         for node in subG.nodes():
              if node not in node_levels:
                   node_levels[node] = -1 # Indicate level couldn't be determined


    return subG, node_levels


def plot_graph(G, root, levels=None, node_levels=None, filter_type=None, silent=False):
    """
    Plot the dependency graph using matplotlib with root form at center.
    Uses node_levels dict for coloring and shell_layout if provided.
    Saves the graph image to the dependency-graphs folder.
    
    Args:
        silent (bool): If True, only saves the file without displaying the plot
    """
    if G.number_of_nodes() == 0:
        print("Graph is empty, cannot plot.")
        return

    plt.figure(figsize=(14, 10))  # Slightly larger figure size

    # Use shell_layout if node_levels are available for distinct levels and there's more than just the root
    pos = None
    if node_levels is not None and G.number_of_nodes() > 1:
        try:
            # Group nodes by level
            # Ensure we only consider nodes that are actually in the graph G
            nodes_in_G = set(G.nodes())
            # Get unique non-negative levels present in G and sort them
            levels_in_G = sorted(list(set(level for node, level in node_levels.items() if node in nodes_in_G and level >= 0)))

            # Create shells: a list of lists, where each inner list is a level's nodes
            shells = [[node for node, level in node_levels.items() if node in nodes_in_G and level == l] for l in levels_in_G]

            # Ensure the root node's shell (level 0) is the first shell if it exists
            # shell_layout requires all nodes in G to be in the shells list.
            all_shell_nodes = set(node for shell in shells for node in shell)
            if shells and root in shells[0] and all_shell_nodes == nodes_in_G:
                print(f"Using shell layout with {len(shells)} levels...")
                pos = nx.shell_layout(G, shells)
            else:
                 print(f"Could not prepare shells for shell_layout (root not in level 0 shell or nodes mismatch). Falling back to spring layout.")
                 pos = None # Force fallback

        except Exception as e:
            print(f"Shell layout failed ({e}), using spring layout instead.")
            pos = None # Force fallback

    # Fallback to spring layout if shell_layout was not used or failed
    if pos is None:
        print("Using spring layout.")
        # Increased k and iterations slightly for potentially better spacing
        pos = nx.spring_layout(G, k=0.7, iterations=150)


    # Determine node colors based on levels if node_levels is available
    node_colors = []
    node_list = list(G.nodes()) # Get the list of nodes in the subgraph for consistent ordering

    if node_levels is not None:
        for node in node_list: # Iterate through the list of nodes in the subgraph
            level = node_levels.get(node) # Get level, will be None if node is not in node_levels
            if level is not None:
                if level == 0:
                    node_colors.append('red')        # Root
                elif level == 1:
                    node_colors.append('lightblue')  # Level 1 children
                elif level == 2:
                    node_colors.append('lightgray')  # Level 2 grandchildren
                else:
                    # Default color for levels > 2 (if any)
                    node_colors.append('lightgreen')
            else:
                # This case should ideally not happen if node_levels is correctly built for all nodes in subG
                # print(f"Warning: Level not found in node_levels for node {node}, defaulting color (Orange).")
                node_colors.append('orange') # Use a distinct color to spot issues
    else:
        # Original coloring logic for when node_levels is None (e.g., 'all levels')
        node_colors = ['red' if node == root else 'lightblue' for node in node_list]


    # Draw nodes
    # Explicitly pass nodelist and pos to ensure correct mapping
    if pos is not None:
        nx.draw_networkx_nodes(G, pos,
                               nodelist=node_list, # Use the consistent list of nodes
                               node_color=node_colors,
                               node_size=2500,
                               alpha=0.9,
                               edgecolors='black', # Add black border to nodes
                               linewidths=0.5)

        # Draw edges with arrows
        nx.draw_networkx_edges(G, pos,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=15, # Slightly smaller arrows
                               arrowstyle='->',
                               alpha=0.5) # More transparency

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold') # Adjust font size
    else:
        print("Layout positions not calculated, cannot draw graph.")


    # Add title
    level_title = levels if levels is not None else 'all'
    filter_title = " (Reports only)" if filter_type == 'R' else " (Forms/Screens only)" if filter_type == 'F' else " (Forms and Reports)"
    plt.title(f"Dependencies for {root} (Levels: {level_title}){filter_title}", fontsize=16)

    plt.axis('off')  # Hide axes
    plt.tight_layout()  # Adjust layout to prevent labels overlapping

    # Create the dependency-graphs directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependency-graphs")
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename based on parameters
    level_part = f"LEVELS_{level_title}"
    type_part = f"TYPE_{filter_type}" if filter_type else "TYPE_ALL"
    filename = f"{root}_{level_part}_{type_part}.png"
    filepath = os.path.join(output_dir, filename)

    # Save the plot
    plt.savefig(filepath, bbox_inches='tight', dpi=300)
    print(f"Graph saved to: {filepath}")

    if not silent:
        plt.show()
    
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Generate a visual dependency graph for a given form.")
    parser.add_argument("-form", "--form", required=True, help="The parent form ID to visualize (case-insensitive).")
    parser.add_argument(
        "-csv",
        "--csvfile",
        default=None,
        help="CSV file with parent-child relationships (default: form_relationships.csv in script directory)."
    )
    parser.add_argument(
        "-levels",
        "--levels",
        type=int,
        default=None,
        help="Number of child levels to include (e.g., 2 for direct children and their children). Default: all levels."
    )
    # Add the new type filter argument
    parser.add_argument(
        "-type",
        "--type",
        choices=['R', 'F'],
        help="Filter relationships by type: 'R' for Reports (child node must match a report prefix), 'F' for Forms/Screens (both parent and child must NOT match a report prefix). Default: Include all."
    )
    parser.add_argument('-silent', action='store_true', help='Save plot without displaying')
    args = parser.parse_args()

    # Determine the CSV file path
    if args.csvfile:
        csv_path = args.csvfile
    else:
        # Use the directory of the script for the default CSV location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "form_relationships.csv")

    form_id = args.form.strip().upper()
    levels = args.levels
    filter_type = args.type # 'R', 'F', or None

    print(f"Reading relationships from: {csv_path}")
    all_relationships = read_relationships(csv_path)
    print(f"Read {len(all_relationships)} total relationships.")

    # --- Filtering Logic ---
    filtered_relationships = []
    if filter_type == 'R':
        print("Filtering for relationships where the CHILD is a Report...")
        for parent, child in all_relationships:
            # Include relationship only if the child is a report based on prefix list
            if is_report(child):
                filtered_relationships.append((parent, child))
    elif filter_type == 'F':
        print("Filtering for relationships where BOTH Parent and Child are Forms/Screens...")
        for parent, child in all_relationships:
             # Include relationship only if both parent and child are forms/screens
            if not is_report(parent) and not is_report(child):
                filtered_relationships.append((parent, child))
    else:
        print("Including all relationship types.")
        filtered_relationships = all_relationships # Use all relationships

    print(f"Using {len(filtered_relationships)} filtered relationships to build the graph.")
    # --- End Filtering Logic ---


    print("Building graph...")
    G = build_graph(filtered_relationships) # Build graph from filtered relationships
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # Check if the specified form_id exists in the FILTERED graph
    if form_id not in G.nodes:
        print(f"Error: Root form ID '{form_id}' not found in the filtered graph nodes.")
        if filter_type:
            # Provide more context if filtering was applied
            print(f"This could be because '{form_id}' was filtered out based on the '-type {filter_type}' flag or it was not present in the original relationships.")
            if filter_type == 'R':
                 print(f"For '-type R', only relationships where the CHILD is a Report are included. Your root '{form_id}' might not be a child in any such relationship.")
            elif filter_type == 'F':
                 print(f"For '-type F', only relationships where BOTH Parent and Child are Forms/Screens are included. Your root '{form_id}' might be a Report or only connected to Reports.")

        print("Available nodes in filtered graph (sample):", list(G.nodes())[:20])
        sys.exit(1)

    # --- Logic for Subgraph Selection and Level Tracking ---
    subG = nx.DiGraph() # Initialize subgraph
    node_levels = None # Initialize node_levels dictionary

    if levels is None:
        # No levels specified, get all descendants and calculate shortest path levels
        print(f"Visualizing all descendants for root form: {form_id}")
        subG, node_levels = get_descendants_subgraph(G, form_id) # get_descendants_subgraph returns levels too
    elif levels >= 0:
        # Specific levels specified (including 0), use get_descendants_limited
        print(f"Visualizing descendants for root form: {form_id} up to level {levels}")
        subG, node_levels = get_descendants_limited(G, form_id, levels) # get_descendants_limited returns levels too
    else:
         print(f"Error: Invalid levels specified ({levels}). Levels must be a non-negative integer or omitted.")
         sys.exit(1)
    # --- End Logic ---


    if subG.number_of_nodes() == 0:
        # Handle case where subgraph is empty
        print(f"No nodes to display for root form '{form_id}' at the specified levels ({levels}) in the filtered graph.")
        # If the root exists in the filtered graph G but the subgraph is empty (e.g., no descendants found)
        if form_id in G.nodes():
             print(f"Plotting only the root node '{form_id}' (from the filtered graph).")
             single_node_graph = nx.DiGraph()
             single_node_graph.add_node(form_id)
             # Create a minimal node_levels dict for the single root node case
             single_node_levels = {form_id: 0}
             # Pass levels and node_levels to plot_graph even for single node
             plot_graph(single_node_graph, form_id, levels, single_node_levels, filter_type, args.silent) # Pass filter_type
        # Note: If form_id wasn't in the filtered graph G at all, the earlier check would have caught it.
        sys.exit(0) # Exit successfully after handling empty graph

    # Pass the computed subgraph, root, levels, node_levels, and filter_type to plot_graph
    plot_graph(subG, form_id, levels, node_levels, filter_type, args.silent)

if __name__ == "__main__":
    main()
