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
  
