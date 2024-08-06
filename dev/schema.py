import os
import json
import logging
from substrate import Substrate, ComputeText, ComputeJSON, sb

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration setup
CONFIG_DIR = os.path.expanduser('~/.config/substrate')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_or_create_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logging.info(f"Config loaded from {CONFIG_FILE}")
            return config
        else:
            api_key = input("Please enter your Substrate API key: ")
            config = {'api_key': api_key}
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            logging.info(f"Config file created at {CONFIG_FILE}")
            return config
    except Exception as e:
        logging.error(f"Error loading or creating config: {str(e)}")
        return None

# Load configuration
config = load_or_create_config()
if not config:
    raise Exception("Failed to load or create configuration")

# Initialize Substrate client
substrate = Substrate(api_key=config['api_key'])

# Define the input query
query = """Hippy types who buy chips and guac, and kale, who are are sporatic in buying during sales, having at least ordered 20 times via app, over total 50 times in e-comm and spend at least 200 to 400 dollars at a time, and drive mini vans with peace signs"""

# Entity schema
entity_schema = {
    "type": "object",
    "properties": {
        "customer_type": {
            "type": "string",
            "description": "Whether STORE ONLY, ONLINE or OMNI (Both STORE and ONLINE) transactions to consider"
        },
        "time_period": {
            "type": ["string", "null"],
            "description": "Date Range user wants to look for audience data (Month, Year)/(mm/dd/yyyy)/(mm/dd/yy)"
        },
        "persona": {
            "type": ["string", "null"],
            "description": "The persona of customer user intends to target. Force persona at all costs."
        },
        "dept": {
            "type": ["string", "null"],
            "description": "The Retail department or Item type user intends to focus on"
        },
        "customer_gen": {
            "type": ["string", "integer", "null"],
            "description": "Any specific age range of customers to focus or Generation name"
        },
        "order_frequency": {
            "type": ["object", "null"],
            "properties": {
                "app": {"type": "integer"},
                "ecommerce": {"type": "integer"}
            },
            "description": "Any specific mention of number of customer orders on respective channel"
        },
        "dollar_amount": {
            "type": ["object", "null"],
            "properties": {
                "minimum": {"type": "integer"},
                "maximum": {"type": "integer"}
            },
            "description": "Any specific mention of minimum or maximum dollar spend. If a single amount is mentioned, use 0 for minimum and the amount for maximum"
        },
        "customer_preference": {
            "type": ["string", "null"],
            "description": "Any mention of customer risk (churn) or propensity/affinity towards something (HIGH/LOW etc)"
        },
        "other_entity": {
            "type": ["object", "null"],
            "description": "Any other important entities user mentions other than above in the query",
            "properties": {
                "vehicle": {"type": "string"},
                "enviromential_index": {"type": "integer"}
            },
        }
    },
    "required": ["customer_type"]
}

# Extraction directive
extraction_directive = """
Extract entities from the given query according to the following schema and guidelines:

1. customer_type (required): Specify whether transactions are STORE ONLY, ONLINE, or OMNI (both store and online).
2. time_period: Extract any date range mentioned for audience data. Format can be Month/Year, mm/dd/yyyy, or mm/dd/yy.
3. persona: Identify the target customer persona, from the query. Force extraction if possible.
4. dept: Specify the retail department or item type focused on in the query.
5. customer_gen: Extract any mentioned age range or generation name for the target customers.
6. order_frequency: Capture the number of customer orders, specifying the channel (app, ecommerce, or total) if mentioned.
7. dollar_amount: Use 0 for minimum and the amount for maximum if only one value is present, both integers.
8. customer_preference: Identify any mentions of customer risk (e.g., churn) or propensity/affinity, including HIGH/LOW indicators if present.
9. other_entity: Capture any other important entities mentioned that don't fit into the above categories.

Ensure all relevant entities are extracted accurately and the output adheres to the given schema. If an entity is not mentioned in the query, set its value to null. For order_frequency and dollar_amount, use object structures as defined in the schema.

Return only the JSON object, no additional text.
"""

# Step 1: Use ComputeText with Llama3Instruct405B
llama_prompt = f"""
{extraction_directive}

QUERY: {query}

SCHEMA:
{json.dumps(entity_schema, indent=2)}
"""

llama_text = ComputeText(prompt=llama_prompt, model="Llama3Instruct405B")
res = substrate.run(llama_text)

# Get the output
output = res.get(llama_text)

print("Output from Llama3Instruct405B:")
print(output.text)

# Attempt to parse the output as JSON
try:
    parsed_json = json.loads(output.text)
    print("\nParsed JSON:")
    print(json.dumps(parsed_json, indent=2))
except json.JSONDecodeError:
    print("\nThe output is not valid JSON. Falling back to ComputeJSON with Llama3Instruct8B.")
    
    # Fallback to ComputeJSON with Llama3Instruct8B
    json_node = ComputeJSON(
        prompt=sb.concat(
            extraction_directive,
            "\n\nQUERY: ", query,
            "\n\nPREVIOUS ATTEMPT:\n", output.text,
            "\n\nPlease correct and format the above attempt as a valid JSON object according to the schema."
        ),
        json_schema=entity_schema,
        model="Llama3Instruct8B"
    )
    
    json_res = substrate.run(json_node)
    json_output = json_res.get(json_node)
    
    print("\nCorrected JSON output:")
    print(json.dumps(json_output.json_object, indent=2))
