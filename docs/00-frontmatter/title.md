# Overview

This document collects the Spatial Ninjas literature summaries, synthesis notes, and next steps.


Project OVERVIEW (updated 13/04 2026)

LLM models chosen for this project: GPT and Gemini.  
Gemma3 is being used for testing purposes in the Test_LLM_for_routing.py as example, although the code can be used for any LLM. 
Routingpy Module is being used as Ground Truth while a certain area of Helsinki from Open Street Map (OSM) is chosen as the reference map. 

Our Current Script Inventory
Our team had developed three scripts that connect raw map data with AI-driven navigation:

   Data Processing (network_to_ssal.py):
   We extract road data from OpenStreetMap (OSM) for Southern Helsinki.
   To save tokens, we convert complex geographical data into SSAL (Simplified Semantic Adjacency List).
   SSAL only keeps essentials: Node IDs, street names, lengths, and one-way status.

   The Engine (Test_LLM_for_routing.py):
   This is the algorithm that feeds the SSAL data and a routing prompt to the LLM.
   It asks the LLM to act as a GPS and output a route in JSON format.

   The Interface (app.py):
   A GUI that allows us to compare OpenAI and Gemini models side-by-side.
   It persists all test history in a SQLite database (history.db) for later analysis.

Technical Specs & Data Logic
To keep the models efficient, we have pruned the OSM attributes:

FeatureLogicSSAL FormatNode: Neighbor {Length, Name, Direction}. Minimalist for token efficiency.
Edge FilteringWe keep u, v, name, length, and oneway. 
We discard speed limits, lane counts, and road types.
Node FilteringWe keep osmid and x/y coordinates so the LLM understands "North/South" and relative positions.


Update 15/04 2026

Compare Routes.py was created and succesfully tested. The script takes the JSON output from the GUI after being passed to the LLM, converts the nodes into coordinates, asks the Routingpy algorithm to make the same route and compares both the correct selected nodes as well as distance estimation in percentate.

The following tests were made so far: 

1 Test
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 313984198 (Bulewardi).

Results:  

Gemini 2.5 Flash:  Failed to deliver correct format in response. 

GPT 5.4 Mini:  Node Sequence Accuracy: 66.7%,  Distance Precision: 99.1%

2 Test
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 311112501 (Korkeavuorenkatu).

Results:  

Gemini 2.5 Flash:  Failed to deliver correct format in response. 

GPT 5.4:  Node Sequence Accuracy: 8.1%,  Distance Precision: 2.9%


3 Test
Find path between Origin Node: 25291564 (Bulewardi) to Destination Node: 25291567 (Yrjonkatu).

Results:  

Gemini 2.5 Flash:  Failed to deliver correct format in response. 

GPT 5.4:  Node Sequence Accuracy: 25.0%,  Distance Precision: 24.1%

Comment: It appears that when the tests become more difficult the accuracy significantly diminishes even for GPT 5.4. 
Gemini 2.5 Flash fails everytime to deliver a correct response format and keeps getting stuch with a response looking like this and stops short before delivering the full answer.  

response_text"```json { "origin": "25291564", "  














  
