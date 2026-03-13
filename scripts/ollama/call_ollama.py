#Script for calling llama3 via Ollama server
#Requires Ollama to be installed
#Modified and simplified version inspired by the source code from Manvi et al.  

from openai import OpenAI

def call_ollama(model_name, prompt):
    # Connect to your local Ollama server
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # Obligatory but ignored by Ollama
    )

    try:
        # Send prompt to your local model ex llama3.2:3b 
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,    
            temperature=0     
        )
        
        completion = response.choices[0].message.content.strip()
        return completion  
        
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None, None, str(e)

#Test the function by sending a prompt to llama3.2:3b
completion = call_ollama("llama3.2:3b", "Hey Lama How are you, can you tell me if Oslo is North of the Arctic Circle?")
print(completion)
