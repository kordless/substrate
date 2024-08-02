import json
import requests

def ollama_chat_result(prompt):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.1",  # You can change this to any model you have in Ollama
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()

    full_response = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            try:
                parsed = json.loads(decoded_line)
                if 'message' in parsed:
                    full_response += parsed['message']['content']
            except json.JSONDecodeError:
                print("Failed to parse JSON:", decoded_line)

    print(full_response)

if __name__ == "__main__":
    prompt = "Write some python for a fib sequence"
    print(f"Sending prompt: '{prompt}'\n")
    ollama_chat_result(prompt)