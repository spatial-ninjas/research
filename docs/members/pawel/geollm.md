# GeoLLM: Extracting Geospatial Knowledge from LLMs

## Summary

Manvi et al. uses a programmatic aproach to test the LLM. 
In their code they amongst others generate a large JSON file with prompts with coordinates and geographical names. 
They then ask the LLM with a prefix prompt to answer the questions with a certain number, and they can then evaluate these compared with actual answers from coordinates on an actual map. One of their evaluation methods is the Spearmanr correlation and finding Pearsonr correlation and r^2 value. 

I had written a modified and simplified code based on their source code but a lighter version which takes their existing prompts file and maps, it generates a CSV file with prompt anwers which are then evaluated by the Spearmanr correlation. So far the codes were tested on Gemma 3, while the plan is to test it on Gemini 3.1 Pro, GPT 5.2, DeepSeek and Llama3 as a open source backup.

## Main contribution

...

## Relevance to our project

...
