#Python Script for testing LLM for Routing capabilities via Routingpy module
#Experimental
#First import the Routingpy and lets define a simple route as an example 

import routingpy 
from routingpy import ORS
from routingpy.routers import ORS

# Authenticate with ORS
client = ORS(api_key='your API key')

# Example: From Copenhagen H to Aarhus H
#coords = [[12.5655, 55.6728], [10.2039, 56.1508]]

#route = client.directions(coords, profile='driving-car')
#print(route.geometry)


#Second lets define a geocoder function so we can convert names into coordinates

from geopy.geocoders import Nominatim
from routingpy import ORS

# 1. Geocoding uden nøgle
# 'user_agent' kan være hvad som helst, f.eks. dit projektnavn
geolocator = Nominatim(user_agent="my_llm_routing_project")

def get_coords(city_name):
    location = geolocator.geocode(city_name)
    # Nominatim returnerer (lat, lon), men ORS vil ofte have [lon, lat]
    return [location.longitude, location.latitude]


#Now lets define our prompt and call Gemini (Gemma 3)

def create_routing_prompt(start_name, end_name, start_coords, end_coords):
    """
    Generates a prompt for an LLM to produce a route compatible with routingpy.
    """
    prompt = f"""
    You are a professional GPS navigation system. 
    Calculate a driving route from {start_name} at {start_coords} to {end_name} at {end_coords}.
    
    Provide the route as a sequence of maneuvers. For each maneuver, include:
    1. A clear instruction (e.g., "Turn left onto Vesterbrogade").
    2. The exact GPS coordinates of the turn/waypoint in [longitude, latitude] format.

    Return the output ONLY as a valid JSON list of objects:
    [
      {{"instruction": "Head north on Road X", "point": [12.565, 55.672]}},
      {{"instruction": "At the roundabout, take the 2nd exit", "point": [12.550, 55.680]}}
    ]
    """
    return prompt


#Function to call Gemini
API_Key = "Your API Key for google.generativeai"
import google.generativeai as genai
def call_gemini(API_Key, model, prompt):
    genai.configure(api_key=API_Key)
    model = genai.GenerativeModel(model)
    generation_config = genai.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=2000,
        temperature=0.2
    )
    response = model.generate_content(prompt, generation_config=generation_config)
    completion=response.text

    return completion 




#Create JSON from Gemini Output
import re
import json

def extract_route_json(completion):
 
    try:
        match = re.search(r"\[.*\]", completion, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"Couldnt interpret JSON: {e}")
    return None


#Define names and coordinates (by geocoting function get_coords)
#Example with Aarhus and Copenhagen
start_name = "København H"
end_name = "Aarhus C"
start_coords = get_coords("København H")
end_coords = get_coords("Aarhus C")

promptAarhus = create_routing_prompt(start_name, end_name, start_coords, end_coords)


#Now lets call Gemini 
raw_text = call_gemini(API_Key, "gemma-3-27b-it", promptAarhus)

# Convert it to a list for stathistics
route_list = extract_route_json(raw_text)

#define the ground truth route via Routingpy by the same set of coordinates
coords = [start_coords, end_coords]
route = client.directions(coords, profile='driving-car')

if route_list:
    print(f"Succes! Received {len(route_list)} waypoints.")
    print("First waypoint:", route_list[0])
else:
    print("Fejl: Couldnt extract JSON from the answer.")

#Now lets segment the route we have from Routepy
steps = route.raw['features'][0]['properties']['segments'][0]['steps']
#We take the coordinate for the start of each step
algo_waypoints = [route.geometry[s['way_points'][0]] for s in steps]
print("steps: ", steps, "algo_waypoints: ", algo_waypoints)








#Now Finally time to do Stathistics and compare these
from scipy.stats import pearsonr
#from sklearn.metrics import r2_score

#Extract coordinates from routingpy (Ground Truth)
algo_steps = route.raw['features'][0]['properties']['segments'][0]['steps']
algo_points = [route.geometry[s['way_points'][0]] for s in algo_steps]

# Extract coordinates from your LLM list 
llm_points = [item['point'] for item in route_list]

# Find the shortest distance
min_len = min(len(algo_points), len(llm_points))

# Split into X (Longitude) and Y (Latitude)
x_true = [p[0] for p in algo_points[:min_len]]
y_true = [p[1] for p in algo_points[:min_len]]

x_pred = [p[0] for p in llm_points[:min_len]]
y_pred = [p[1] for p in llm_points[:min_len]]

# Calculate Pearson and R2
corr_x, _ = pearsonr(x_true, x_pred)
corr_y, _ = pearsonr(y_true, y_pred)

r2_x = corr_x ** 2
r2_y = corr_y ** 2

#Print our resulkts
print(f"--- Statistical Analysis (N={min_len}) ---")
print(f"Pearson r (Longitude): {corr_x:.4f}")
print(f"Pearson r (Latitude):  {corr_y:.4f}")
print(f"R² Score (Longitude):  {r2_x:.4f}")
print(f"R² Score (Longitude):  {r2_y:.4f}")



