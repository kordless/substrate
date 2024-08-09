import os
import json
import logging
from substrate import Substrate, ComputeText, sb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_FILE = os.path.expanduser('~/.config/substrate-chat/config.json')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

config = load_config()
api_key = config['api_key']

# Initialize Substrate
logger.info("Initializing Substrate with provided API key.")
substrate = Substrate(api_key=api_key)

# Create initial computations
logger.info("Creating initial computation for GPT-4o.")
response_1 = ComputeText(prompt="Explain quantum mechanics.", model="gpt-4o")
logger.info(f"Attributes and methods of response_1: {dir(response_1)}")

logger.info("Creating initial computation for Claude 3.5 Sonnet.")
response_2 = ComputeText(prompt="Explain quantum mechanics.", model="claude-3-5-sonnet-20240620")
logger.info(f"Attributes and methods of response_2: {dir(response_2)}")

# Access and log details about future.text of each response
logger.info("Accessing future.text for response_1.")
response_1_text_future = response_1.future.text
logger.info(f"response_1 future.text: {response_1_text_future}")

logger.info("Accessing future.text for response_2.")
response_2_text_future = response_2.future.text
logger.info(f"response_2 future.text: {response_2_text_future}")

# Create and log reasoning prompt
reasoning_prompt = sb.format("Based on {response_1} and {response_2}, summarize the main concepts.",
                             response_1=response_1_text_future,
                             response_2=response_2_text_future)
logger.info(f"Reasoning prompt: {reasoning_prompt}")

# Create a reasoning step
reasoning = ComputeText(
    prompt=reasoning_prompt,
    model="Llama3Instruct405B"
)
logger.info(f"Attributes and methods of reasoning: {dir(reasoning)}")
logger.info(f"Reasoning future.text: {reasoning.future.text}")

# Create and log final answer prompt
final_answer_prompt = sb.format("Provide a final summary considering: {reasoning}",
                                reasoning=reasoning.future.text)
logger.info(f"Final answer prompt: {final_answer_prompt}")

# Combine the reasoning into a final answer
final_answer = ComputeText(
    prompt=final_answer_prompt,
    model="Llama3Instruct405B"
)
logger.info(f"Attributes and methods of final_answer: {dir(final_answer)}")
logger.info(f"Final answer future.text: {final_answer.future.text}")

# Execute the entire chain of computations
logger.info("Running the computation chain.")
response = substrate.run(final_answer)

# Log the final answer object and its attributes
logger.info(f"Final answer object: {final_answer}")
logger.info(f"Final answer future.text: {final_answer.future.text}")
