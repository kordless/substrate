import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from substrate import Substrate, ComputeText

app = FastAPI()

# Load configuration
CONFIG_FILE = os.path.expanduser('~/.config/substrate-chat/config.json')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

config = load_config()
api_key = config['api_key']

# Initialize Substrate
substrate = Substrate(api_key=api_key)

@app.get("/chat")
async def chat():
    query = ComputeText(
        prompt="Human: Hello\nAssistant:",
        temperature=0.4,
        max_tokens=800,
        num_choices=1,
        model="Llama3Instruct405B"
    )

    stream = substrate.stream(query)

    async def event_generator():
        for event in stream.iter():
            if isinstance(event, dict):
                yield f"data: {json.dumps(event)}\n\n"
            else:
                yield f"data: {event}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)