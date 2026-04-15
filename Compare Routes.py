#Prompt to give to LLM after having run SSAL network_to_ssal.py and saved SSAL file

"""

System Role: > You are a precise navigation engine. Your task is to calculate the shortest path between two nodes using the provided SSAL (Simplified Semantic Adjacency List) network data.

Input Data:
I have attached a file named network_output.ssal. This file contains the network topology where each line represents a node and its outgoing connections in the format: Node_ID: Neighbor_ID {Length, Name, Direction}.

Task:
Find the optimal route from Origin Node ID: [INSERT START ID] to Destination Node ID: [INSERT END ID].

Constraints:

Only use connections explicitly listed in the SSAL data.

Respect "1w" (one-way) and "2w" (two-way) markers.

Minimize the total "Length".

Output the result strictly as a JSON object.

Output Format:

JSON
{
  "origin": "[ID]",
  "destination": "[ID]",
  "total_length": [FLOAT],
  "route": [
    {"node": "[ID]", "edge_name": "start"},
    {"node": "[ID]", "edge_name": "[STREET NAME]"},
    ...
  ],
  "status": "success"
}
Do not include any conversational text, only the JSON.

"""

#After having run the Prompt and downloaded the JSON history file from the GUI App, this code will be run
#It extracts the response from the JSON, converts the Node ID into coordinates and compares it with the Routepy algorithm for the same routing
#It compares both distances and Nodes and calculates the accuracy score.  

import json
import geopandas as gpd
import numpy as np
import re
from routingpy.routers import ORS

# --- CONFIGURATION ---
GPKG_PATH = "osm_southern_helsinki_slimmed_cropped.gpkg"
HISTORY_JSON = "llm_compare_history.json"
ORS_API_KEY = "your ORS API Key"

def clean_json(text):
    """ Extracts the JSON object from raw text strings. """
    if not text or not isinstance(text, str): 
        return None
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else None

# --- INITIALIZATION ---
client = ORS(api_key=ORS_API_KEY)

print("Step 1: Loading network data...")
try:
    nodes_gdf = gpd.read_file(GPKG_PATH, layer="slimmed_cropped_nodes")
    # Ensure coordinates are stored as floats for mathematical operations
    node_lookup = {str(row["osmid"]): [float(row["x"]), float(row["y"])] for _, row in nodes_gdf.iterrows()}
    print(f"Status: Successfully loaded {len(node_lookup)} nodes.")
except Exception as e:
    print(f"Critical Error: Failed to load GeoPackage. {e}")
    node_lookup = {}

if node_lookup:
    print("\nStep 2: Processing model history...")
    try:
        with open(HISTORY_JSON, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except Exception as e:
        print(f"Critical Error: Failed to load history file. {e}")
        history = []

    for i, entry in enumerate(history):
        model_id = entry.get('id', i)
        
        # Check primary fields for model output
        raw_text = entry.get('response_text') or entry.get('response') or entry.get('text') or ""
        
        json_str = clean_json(str(raw_text))
        if not json_str:
            continue 

        try:
            res = json.loads(json_str)
            path = res.get('path') or res.get('route')
            origin = str(res.get('origin', '')).strip()
            destination = str(res.get('destination', '')).strip()

            if not path or origin not in node_lookup:
                continue

            print(f"\n--- Evaluation for Model ID: {model_id} ---")
            
            # 1. Fetch Ground Truth from OpenRouteService
            locations = [node_lookup[origin], node_lookup[destination]]
            route = client.directions(locations=locations, profile='driving-car')
            
            # 2. Node Sequence Accuracy Calculation
            llm_coords = []
            for step in path:
                nid = str(step.get('node')).strip()
                if nid in node_lookup:
                    llm_coords.append([float(c) for c in node_lookup[nid]])
            
            gt_coords = np.array(route.geometry, dtype=float)
            llm_coords_arr = np.array(llm_coords, dtype=float)
            
            node_accuracy = 0
            if len(llm_coords_arr) > 0 and len(gt_coords) > 0:
                min_len = min(len(llm_coords_arr), len(gt_coords))
                matches = [np.allclose(llm_coords_arr[i], gt_coords[i], atol=1e-4) for i in range(min_len)]
                node_accuracy = sum(matches) / max(len(llm_coords_arr), len(gt_coords))
            
            # 3. Distance Precision Calculation
            try:
                llm_distance = float(res.get('total_length', 0))
                gt_distance = float(route.distance)
                dist_precision = max(0, 1 - (abs(llm_distance - gt_distance) / gt_distance)) if gt_distance > 0 else 0
            except (ValueError, TypeError):
                llm_distance = 0
                dist_precision = 0
            
            print(f"Route: {origin} -> {destination}")
            print(f"Node Sequence Accuracy: {node_accuracy*100:.1f}%")
            print(f"Distance Precision:    {dist_precision*100:.1f}%")
            print(f"Length Comparison: LLM {llm_distance}m | Algorithm {gt_distance:.1f}m")
                
        except Exception as e:
            print(f"Error: Could not process Model ID {model_id}. {e}")
