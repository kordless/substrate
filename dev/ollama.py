import json
import requests

def ollama_chat_raw(prompt):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.1",  # You can change this to any model you have in Ollama
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()

    print("Raw Ollama Output:")
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
            
            # Pretty print the JSON for better readability
            try:
                parsed = json.loads(line)
                print(json.dumps(parsed, indent=2))
                print("-" * 50)
            except json.JSONDecodeError:
                print("Failed to parse JSON:", line.decode('utf-8'))

if __name__ == "__main__":
    prompt = "What is the capital of France?"
    print(f"Sending prompt: '{prompt}'\n")
    ollama_chat_raw(prompt)