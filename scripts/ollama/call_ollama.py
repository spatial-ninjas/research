# Script for calling Llama models via a local Ollama server
# Requires Ollama to be installed and running.
#
# Modified and simplified version inspired by the source code from:
# Manvi et al. (2024), GeoLLM

from openai import OpenAI


def call_ollama(model_name, prompt, max_tokens=50, temperature=0):
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None


if __name__ == "__main__":
    completion = call_ollama(
        "llama3.2:3b",
        "Is Oslo north of the Arctic Circle?"
    )
    print(completion)