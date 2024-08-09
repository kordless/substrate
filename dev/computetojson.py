from substrate import ComputeJSON, ComputeText, sb, Substrate
import json, logging, os

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

# Define the JSON schema
json_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the author."
        },
        "bio": {
            "type": "string",
            "description": "Concise biography of the author."
        }
    }
}

# Create the ComputeJSON node
author = ComputeJSON(
    prompt="Who wrote Don Quixote?",
    json_schema=json_schema,
    temperature=0.4,
    max_tokens=800
)

# Create the ComputeText node using sb.format for string interpolation
report = ComputeText(
    prompt=sb.format("Write a short summary about {name} and make sure to use the following bio: {bio}",
                     name=author.future.json_object["name"],
                     bio=author.future.json_object["bio"])
)

# Note: To execute this computation, you would need to run it with a Substrate instance:
# substrate = Substrate(api_key="your_api_key")
result = substrate.run(report)
print(result.get(report).text)