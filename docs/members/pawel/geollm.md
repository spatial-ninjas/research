# GeoLLM: Extracting Geospatial Knowledge from LLMs

## Summary

Manvi et al. uses a programmatic aproach to test the LLM. 
In their code they amongst others generate a large JSON file with prompts with coordinates and geographical names. 
They then ask the LLM with a prefix prompt to answer the questions with a certain number such as to estimate the population density for a given set of coordinates, and they can then evaluate these compared with actual answers from coordinates on an actual map. One of their evaluation methods is the Spearmanr correlation and finding Pearsonr correlation and r^2 value. The r^2 value is the final number they use to compare the models against each other in their publicaiton. 

I had written a modified and simplified code based on their source code but a lighter version which takes their existing prompts file and maps, it generates a CSV file with prompt anwers which are then evaluated by the Spearmanr correlation. So far the codes were tested on Gemma 3, while the plan is to test it on Gemini 3.1 Pro, GPT 5.2, DeepSeek and Llama3 as a open source backup.

## Main contribution

-Standardized Benchmarking: Implementation of Manvi et al.’s method to quantitatively measure "spatial cognition" in LLMs via coordinate-based prompting.

-Streamlined Pipeline: A lightweight, modified version of the original source code, optimized for faster execution and lower resource consumption.

-Automated Evaluation: Generates a direct CSV output of prompt-responses and calculates Spearmanr correlation automatically.

-Cross-Model Compatibility: A unified test-bench designed to compare performance across diverse models, including Gemma 3, Gemini 3.1 Pro, GPT-5.2, and Llama 3.

## Relevance to our project

The approach of Manvi et al is a concrete method to test the spatial kognition of an LLM and compare it with the performance of different models programatically, and to test them quantitatively.  
