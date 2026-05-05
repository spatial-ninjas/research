LLM Route Test Results (updated 16/04 2026).

The following prompt was used along the SSAL file to ask the LLM:

"""

System Role: > You are a precise navigation engine. Your task is to calculate the shortest path between two nodes using the provided SSAL (Simplified Semantic Adjacency List) network data.

Input Data:
I have attached a file named network_output.ssal. This file contains the network topology where each line represents a node and its outgoing connections in the format: Node_ID: Neighbor_ID {Length, Name, Direction}.

Task:
Find the optimal route from Origin Node ID: [INDSÆT START ID] to Destination Node ID: [INDSÆT SLUT ID].

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

The Results were as follows (updated 16/04 2026, Gemini thinking budget: Dynamic): 


Test 1
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 313984198 (Bulewardi). Max Output Tokens: 300. Number of swings: 0

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4 Mini: Node Sequence Accuracy: 66.7%, Distance Precision: 99.1%

Test 2
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 313984198 (Bulewardi). Max Output Tokens: 512. Number of swings: 0

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4: Node Sequence Accuracy: 66.7%, Distance Precision: 99.1%


Test 3
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 311112501 (Korkeavuorenkatu). Max Output Tokens: 512. Number of swings: 2

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4: Node Sequence Accuracy: 8.1%, Distance Precision: 2.9%

Test 4
Find path between Origin Node: 25291564 (Bulewardi) to Destination Node: 25291567 (Yrjonkatu). Max Output Tokens: 512. Number of swings: 1

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4: Node Sequence Accuracy: 25.0%, Distance Precision: 24.1%

Test 5
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 25291550 (Uudenmaankatu). Max Output Tokens: 1024. Number of swings: 2

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4 Mini: Node Sequence Accuracy: 15.8%, Distance Precision: 4.2%

Test 6
Find path between Origin Node: 313984203 (Bulewardi) to Destination Node: 3232013778 (Annankatu). Max Output Tokens: 1024. Number of swings: 1

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4: Failed to deliver correct format in response.

Test 7
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 3228745582 (Hietalandenventa). Max Output Tokens: 1024. Number of swings: 1

Results:

Gemini 2.5 Flash: Failed to deliver correct format in response.

GPT 5.4: Failed to deliver correct format in response.



Test Update 20/04 2026 (Gemini Thinking Budget: switched off, number of max input tokens varied)

Test 8 
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 25291550 (Uudenmaankatu). Max Output Tokens: 1024. Number of swings: 2

Results:  Gemini 2.5 Flash: Failed to deliver correct format in response (No JSON found).

GPT 5.4: Failed - Path empty or Origin Node not in network.

Test 9 
Find path between Origin Node: 25291564 (Bulewardi) to Destination Node: 25291567 (Yrjonkatu). Max Output Tokens: 1024. Number of swings: 1

Results:  Gemini 2.5 Flash: Failed to deliver correct format in response (No JSON found).

GPT 5.4: Node Sequence Accuracy: 25.0%, Distance Precision: 15.1% (Length: LLM 16.0m | Algorithm 106.0m).

Test 10 
Find path between Origin Node: 25291564 (Bulewardi) to Destination Node: 25291567 (Yrjonkatu). Max Output Tokens: 2048. Number of swings: 1

Results: Gemini 2.5 Flash: Failed to deliver correct format in response (No JSON found).

GPT 5.4: Node Sequence Accuracy: 25.0%, Distance Precision: 38.5% (Length: LLM 40.8m | Algorithm 106.0m).

Test 11
Find path between Origin Node: 25291564 (Bulewardi) to Destination Node: 25291567 (Yrjonkatu). Max Output Tokens: 1600. Number of swings: 1

Results:  Gemini 2.5 Flash: Node Sequence Accuracy: 25.0%, Distance Precision: 10.2% (Length: LLM 10.8m | Algorithm 106.0m).

GPT 5.4: Node Sequence Accuracy: 25.0%, Distance Precision: 24.1% (Length: LLM 25.5m | Algorithm 106.0m).

Test 12
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 25291550 (Uudenmaankatu). Max Output Tokens: 1600. Number of swings: 2

Results:  Gemini 2.5 Flash: Node Sequence Accuracy: 11.5%, Distance Precision: 26.4% (Length: LLM 69.1m | Algorithm 262.0m).

GPT 5.4: Failed - Path empty or Origin Node not in network.


NEW TESTS WITH UPDATED SSAL FILE (22/04 2026)

Test 13
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 25291550 (Uudenmaankatu). Max Output Tokens: 1600. Number of swings: 2

Results:  Gemini 2.5 Flash: Node Sequence Accuracy: 12.0%, Distance Precision: 25.5% (Length: LLM 66.8m | Algorithm 262.0m).

GPT 5.4 Mini: Node Sequence Accuracy: 15.8%  Distance Precision: 6.4% (Length: LLM 16.7m | Algorithm 262.0m)

Test 14
Find path between Origin Node: 25291564 (Bulewardi) to Destination Node: 25291567 (Yrjonkatu). Max Output Tokens: 1600. Number of swings: 1

Results:  Gemini 2.5 Flash: Node Sequence Accuracy: 25.0%, Distance Precision: 65.4% (Length: LLM 69.3m | Algorithm 106.0m).

GPT 5.4: Node Sequence Accuracy: 25.0%  Distance Precision: 93.9% (Length: LLM 112.5m | Algorithm 106.0m)

Test 15
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 3228745582 (Hietalandenventa). Max Output Tokens: 1600. Number of swings: 1

Results:  Gemini 2.5 Flash: Failed to deliver correct response format.

GPT 5.4:  Failed to deliver correct response format. 

Test 16
Find path between Origin Node: 313984203 (Bulewardi) to Destination Node: 3232013778 (Annankatu). Max Output Tokens: 1600. Number of swings: 1

Results:  Gemini 2.5 Flash: Failed to deliver correct response format. 

GPT 5.4: Node Sequence Accuracy: 16.0%  Distance Precision: 46.3% (Length: LLM 120.8m | Algorithm 261.0m)

Test 17
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 311112501 (Korkeavuorenkatu). Max Output Tokens: 1600. Number of swings: 2

Results:  Gemini 2.5 Flash: Failed to deliver correct response format.

GPT 5.4: Node Sequence Accuracy: 5.4%  Distance Precision: 49.5% (Length: LLM 291.0m | Algorithm 588.0m)

Test 18
Find path between Origin Node: 25291537 (Bulewardi) to Destination Node: 313984198 (Bulewardi). Max Output Tokens: 1600. Number of swings: 0

Results:  Gemini 2.5 Flash: Node Sequence Accuracy: 66.7%, Distance Precision: 99.1% (Length: LLM 11.1m | Algorithm 11.0m).

GPT 5.4: Node Sequence Accuracy: 66.7%  Distance Precision: 99.1% (Length: LLM 11.1m | Algorithm 11.0m)


UPDATE 05-05-2026 Tests with different Prompt Templates.  

LLM Route Test Results (Updated 04/05 2026 - Complete Session)
Test 19 | 18:21:05 | Route: 1004552350 → 9713069615. Swings: 0

Prompt Template: JSON Generator

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 87.5%, Precision: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 87.5%, Precision: N/A

Test 20 | 18:27:05 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: JSON Generator

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 66.7%, Precision: N/A

Test 21 | 18:27:28 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: N/A

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 66.7%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 22 | 18:27:33 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: JSON Generator

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 66.7%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 23 | 18:28:44 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: JSON Generator

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 25.0%, Precision: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 33.3%, Precision: N/A

Test 24 | 18:29:07 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: JSON Generator

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 25.0%, Precision: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Test 25 | 18:29:31 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: JSON Generator

gpt-5.4-mini: ⚠️ Needs review. Accuracy: 25.0%, Precision: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Test 26 | 18:29:47 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: JSON Generator

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 16.7%, Precision: -194.9%

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 27 | 18:33:12 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: Validation Routing Engine

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 28 | 18:33:19 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: Validation Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 100.0%, Precision: N/A

Test 29 | 18:33:26 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: Validation Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 30 | 18:34:31 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: Validation Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Test 31 | 18:34:41 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: Validation Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 91.7%, Precision: N/A

Test 32 | 18:34:54 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: N/A

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 16.7%, Precision: -194.9%

Test 33 | 18:35:35 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: Validation Routing Engine

gpt-5.4: ⚠️ Needs review. Accuracy: 7.7%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 34 | 18:36:00 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: Validation Routing Engine

gpt-5.4: ⚠️ Needs review. Accuracy: 3.8%, Precision: N/A

Test 35 | 18:36:01 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Test 36 | 18:36:09 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: Validation Routing Engine

gpt-5.4: ⚠️ Needs review. Accuracy: 7.7%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 37 | 18:39:02 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: Node to Node Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 33.3%, Precision: N/A

Test 38 | 18:39:08 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: Node to Node Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 39 | 18:39:16 | Route: 25291537 → 313984198. Swings: 0

Prompt Template: Node to Node Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 40 | 18:40:03 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: Node to Node Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 41 | 18:40:04 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 16.7%, Precision: -194.9%

Test 42 | 18:40:13 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: Node to Node Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: 16.7%, Precision: -194.9%

Test 43 | 18:40:35 | Route: 25291564 → 25291567. Swings: 1

Prompt Template: Node to Node Routing Engine

gpt-5.4: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Test 44 | 18:41:26 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: Node to Node Routing Engine

gpt-5.4: ⚠️ Needs review. Accuracy: 3.8%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 45 | 18:41:46 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: Node to Node Routing Engine

gpt-5.4: ⚠️ Needs review. Accuracy: 3.8%, Precision: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Test 46 | 18:41:52 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: Node to Node Routing Engine

gpt-5.4: ⚠️ Needs review. Accuracy: 3.8%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 47 | 18:44:16 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: N/A

gpt-5.4: ⚠️ Needs review. Accuracy: 7.7%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 48 | 18:44:37 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: JSON Generator

gpt-5.4: ⚠️ Needs review. Accuracy: 7.7%, Precision: N/A

gemini-2.5-flash: ✅ Satisfactory. Accuracy: 100.0%, Precision: 100.0%

Test 49 | 18:45:13 | Route: 25291537 → 25291550. Swings: 2

Prompt Template: JSON Generator

gpt-5.4: ⚠️ Needs review. Accuracy: 7.7%, Precision: N/A

gemini-2.5-flash: ⚠️ Needs review. Accuracy: N/A, Precision: N/A

Prompt Templates: 

Template Name: JSON Generator

"""
You are a JSON generator. Your absolute priority is to return a valid JSON object without any syntax errors.

Task:
Calculate the shortest route from Origin Node ID: {origin} to Destination Node ID: {destination} using the SSAL data.

Strict Formatting Rules:
- The output MUST start with {{ and end with }}.
- Do NOT add markdown code fences (like ```json).
- Do NOT write any natural language or explanations before or after the JSON.
- Ensure all quotes are standard double quotes.

Output format:
{{
  "origin": "{origin}",
  "destination": "{destination}",
  "total_length": 0.0,
  "route": [
    {{"node": "{origin}", "edge_name": "start"}},
    {{"node": "[ID]", "edge_name": "[STREET NAME]"}}
  ],
  "status": "success"
}}

Here is the SSAL network data to use for your calculation:
{ssal_text}
"""

Template Name: VALIDATION ROUTING ENGINE

"""
You are a graph validation routing engine. Your task is to calculate the shortest path from Origin Node ID: {origin} to Destination Node ID: {destination}.

Strict Routing Rules:
1. NO HALLUCINATION: Only use connections explicitly listed in the SSAL data.
2. ONE-WAY VALIDATION: For every node you visit, you must verify that the connection has a "2w" flag, or that your movement aligns with the allowed direction if it is "1w".
3. CONTINUOUS PATH: Each node in the sequence must have an explicit connection to the next node in the data.

Output the final valid JSON directly without any extra text, code fences, or explanations.

Output format:
{{
  "origin": "{origin}",
  "destination": "{destination}",
  "total_length": 0.0,
  "route": [
    {{"node": "{origin}", "edge_name": "start"}},
    {{"node": "[ID]", "edge_name": "[STREET NAME]"}}
  ],
  "status": "success"
}}

Here is the SSAL network data to use for your calculation:
{ssal_text}
"""

Template Name: NODE TO NODE Routing Engine.  

"""
You are a precise node-to-node routing engine. You must strictly ground your calculation in the SSAL data and ignore spatial heuristics.

Grounding Rules:
- Treat the graph purely as abstract node IDs and edge lengths.
- Do NOT make assumptions based on node coordinates or road names.
- Only trace the route step-by-step using explicitly stated source-to-target links.
- Do not invent connections that are not listed under the current source node.

Output the result strictly as a valid JSON object. No explanation, markdown, or code fences.

Output format:
{{
  "origin": "{origin}",
  "destination": "{destination}",
  "total_length": 0.0,
  "route": [
    {{"node": "{origin}", "edge_name": "start"}},
    {{"node": "[ID]", "edge_name": "[STREET NAME]"}}
  ],
  "status": "success"
}}

Here is the SSAL network data to use for your calculation:
{ssal_text}
"""

Comments about Results. 

Our results in short show the following numbers:

JSON Generator: 10 tests| Gemini 100% correct: 4 | GPT 100% correct: 0.
Validation Routing Engine: 10 tests | Gemini 100% correct: 4 | GPT 100% correct: 6.
Node to Node Routing Engine: 10 tests | Gemini 100% correct: 5 | GPT 100% correct: 5.
N/A (Baseline/Control): 5 tests | Gemini 100% correct: 2 | GPT 100% correct: 1.

Results show a clear correlation between prompt strategy and routing logic. The baseline and JSON Generator variants often fail on complex paths because the models prioritize format over network topology.

Gemini 2.5 Flash thrives with the Validation Routing Engine and Node to Node Routing Engine prompts. By forcing the model to ignore spatial heuristics and strictly verify "1w/2w" flags, we eliminated previous formatting errors and achieved 100% accuracy on difficult 2-swing routes. This suggests Gemini is highly capable of graph traversal when stripped of "geographical intuition."

GPT 5.4 remains more robust regarding output structure across all variants but consistently struggles with the underlying logic. Even with strict grounding rules, it frequently hallucinates connections or provides a valid JSON format for an impossible path.

In conclusion, the Validation Routing Engine prompt is currently the most effective for production, as it successfully forces the models to treat the SSAL data as a mathematical graph rather than a creative writing task. Gemini is the preferred engine for complex navigation, while GPT serves better for simple, high-speed formatting tasks.




