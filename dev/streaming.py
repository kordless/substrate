import asyncio
import os
import json
import logging
from substrate import Substrate, Llama3Instruct70B

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_DIR = os.path.expanduser('~/.config/substrate-chat')
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

async def amain():
    # Load configuration
    config = load_or_create_config()
    if not config:
        logging.error("Failed to load or create config. Exiting.")
        return

    api_key = config.get('api_key')
    if not api_key:
        logging.error("API key not found in config. Exiting.")
        return

    try:
        # Initialize Substrate client with the API key from config
        substrate = Substrate(api_key=api_key, timeout=60 * 5)

        # Define the query using Llama3Instruct70B
        query = Llama3Instruct70B(
            prompt="Who is Don Quixote?",
            num_choices=2,
            temperature=0.4,
            max_tokens=800
        )

        # Start the stream
        response = await substrate.async_stream(query)
        async for event in response.async_iter():
            print(event)

    except Exception as e:
        logging.error(f"Error in Substrate async streaming: {str(e)}")

if __name__ == "__main__":
    asyncio.run(amain())
