# Calling local LLMs with Ollama

This directory contains a small helper script for sending prompts to a **locally running Ollama model** using the OpenAI-compatible API exposed by Ollama.

The script can be used to quickly test prompts or to integrate local LLM inference into experiments.

## Script

```
call_ollama.py
```

This script defines a helper function:

```
call_ollama(model_name, prompt, max_tokens=50, temperature=0)
```

It sends a prompt to a locally running Ollama model and returns the generated text.


# Prerequisites

Before running the script, Ollama must be installed and a model must be available locally.

## 1. Install Ollama

Follow the instructions at:

https://ollama.com

Example installation command:

```
curl -fsSL https://ollama.com/install.sh | sh
```

Depending on your system, installation may require elevated permissions.

Verify the installation:

```
ollama --version
```

Example:

```
ollama version is 0.17.7
```


## 2. Pull the model

Download the model used by the script:

```
ollama pull llama3.2:3b
```

You can check installed models with:

```
ollama list
```

Example:

```
NAME           ID              SIZE
llama3.2:3b    a80c4f17acd5    2.0 GB
```


## 3. Ensure the Ollama server is running

Ollama exposes an HTTP API on port **11434**.

In many cases the server starts automatically during installation.

If you run:

```
ollama serve
```

and see:

```
Error: listen tcp 127.0.0.1:11434: bind: address already in use
```

this usually means the server is **already running**, which is expected.

You can test the model directly:

```
ollama run llama3.2:3b
```

Example prompt:

```
Is Oslo north of the Arctic Circle?
```


# Python dependency

The script uses the OpenAI Python client to communicate with the Ollama API.

Install it with:

```
pip install openai
```


# How the script works

Ollama exposes an **OpenAI-compatible API** locally at:

```
http://localhost:11434/v1
```

The script connects to this endpoint using the OpenAI Python client.

Example connection:

```
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
```

The API key is required by the client library but ignored by Ollama.


# Running the script

From the repository root:

```
python scripts/ollama/call_ollama.py
```

Example output:

```
No, Oslo is south of the Arctic Circle.
```


# Using the function in other scripts

The helper function can also be imported into other Python modules.

Example:

```
from scripts.ollama.call_ollama import call_ollama

response = call_ollama(
    "llama3.2:3b",
    "Is Helsinki north of Berlin?"
)

print(response)
```


# Notes

* The model runs **locally** on your machine.
* Model responses are **not guaranteed to be factually correct**.
* This script is intended as a simple helper for testing and experimentation.
* If local inference becomes a larger part of the repository, this functionality should later be moved into a dedicated module.
