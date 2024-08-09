import os
import json
import logging
from substrate import Substrate, ComputeText, sb, ComputeJSON

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_FILE = os.path.expanduser('~/.config/substrate/config.json')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

config = load_config()
api_key = config['api_key']

substrate = Substrate(api_key=api_key)

# ComputeText example
text_prompt = "Explain quantum entanglement briefly. provide name year description."
text_node = ComputeText(prompt=text_prompt, model="gpt-4o")

# ComputeJSON example
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "year": {"type": "integer"},
        "description": {"type": "string"}
    },
    "required": ["name", "year", "description"]
}

json_prompt = sb.format("""
    translate to the following to a target schema. Based on the explanation: {text}
""", text=text_node.future.text) 
print(json_prompt)

json_node = ComputeJSON(
    prompt=json_prompt,
    model="Mixtral8x7BInstruct",
    json_schema=json_schema
)

# Execute the computation chain
result = substrate.run(json_node)

# Log results
logger.info(f"Text explanation: {result.get(text_node).text}")
logger.info(f"JSON output: {json.dumps(result.get(json_node).json_object, indent=2)}")