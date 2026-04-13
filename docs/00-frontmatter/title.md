# Overview

This document collects the Spatial Ninjas literature summaries, synthesis notes, and next steps.


Project OVERVIEW (updated 13/04 2026)


1. Our Current Script Inventory
   Our team had developed three scripts that connect raw map data with AI-driven navigation:

   Data Processing (network_to_ssal.py):
   -We extract road data from OpenStreetMap (OSM) for Southern Helsinki.
   -To save tokens, we convert complex geographical data into SSAL (Simplified Semantic Adjacency List).
   -SSAL only keeps essentials: Node IDs, street names, lengths, and one-way status.

   The Engine (Test_LLM_for_routing.py):
   -This is the algorithm that feeds the SSAL data and a routing prompt to the LLM (Gemma 3).
   It asks the LLM to act as a GPS and output a route in JSON format.

   The Interface (app.py):
   -A GUI that allows us to compare OpenAI and Gemini models side-by-side.
   -It persists all test history in a SQLite database (history.db) for later analysis.

2. Technical Specs & Data Logic
To keep the models efficient, we have pruned the OSM attributes:

FeatureLogicSSAL FormatNode: Neighbor {Length, Name, Direction}. Minimalist for token efficiency.Edge FilteringWe keep u, v, name, length, and oneway. We discard speed limits, lane counts, and road types.Node FilteringWe keep osmid and x/y coordinates so the LLM understands "North/South" and relative positions.
  
