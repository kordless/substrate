from substrate import Substrate
from substrate import ComputeText, ComputeJSON, sb
import os
import logging
import json
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def list_files():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    return files

def get_file_content(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_file_content(file_path, content):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f"Successfully wrote changes to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error writing to file {file_path}: {str(e)}")
        return False

config = load_or_create_config()
if not config:
    logging.error("Failed to load or create config. Exiting.")
    exit(1)

api_key = config.get('api_key')
if not api_key:
    logging.error("API key not found in config. Exiting.")
    exit(1)

substrate = Substrate(api_key=api_key)

models = [
    "gpt-4o-mini",
    "Llama3Instruct8B",
    "Mixtral8x7BInstruct"
]

def run_comparison(is_retry=False, compute_texts=None, reasoning=None, prompt=None, file_content=None, selected_file=None):
    if not is_retry:
        logging.info(f"Selected models: {', '.join(models)}")

        # List files and get user selection
        files = list_files()
        while True:
            try:
                choice = int(input("Enter the number of the file you want to use: "))
                if 1 <= choice <= len(files):
                    selected_file = files[choice - 1]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        # Get file content
        file_content = get_file_content(selected_file)
        if not file_content:
            logging.error("Failed to read file content. Exiting.")
            exit(1)

        # Get user's desired change
        prompt = input("Enter the change you want to make to the code (e.g., 'increase the resolution by a factor of 2 in both dimensions'): ")

        try:
            compute_texts = [ComputeText(
                prompt=sb.concat(
                    "Make the following change to the code:\n", prompt,
                    "\n\nOriginal code:\n", file_content
                ),
                model=model
            ) for model in models]

            reasoning = ComputeText(
                prompt=sb.concat(
                    "Reason about the strengths and weaknesses of each diff response. Explain which elements from each diff response are superior.",
                    "\nPROMPT: ", prompt,
                    "\nORIGINAL CODE:\n", file_content,
                    "\nCANDIDATE RESPONSES:",
                    *[f"\n{i+1}) {ct.future.text}" for i, ct in enumerate(compute_texts)]
                )
            )
        except Exception as e:
            logging.error(f"Error occurred during initial computation: {str(e)}")
            return

    retry_instruction = "The previous attempt did not produce a valid unified diff. Please ensure you generate a proper unified diff this time. " if is_retry else ""

    answer = ComputeText(
        prompt=sb.concat(
            retry_instruction,
            "Come up with a detailed, comprehensive, unified diff using the best parts of the candidate responses, based on the evaluation. ",
            "Return only a diff response, do not reveal the process (do not say candidate response or evaluation). ",
            "Ensure the output is in the format of a unified diff, with lines starting with '+', '-', or ' ' (space) to indicate changes.",
            "\nPROMPT: ", prompt,
            "\nORIGINAL CODE:\n", file_content,
            "\nCANDIDATE RESPONSES:",
            *[f"\n{i+1}) {ct.future.text}" for i, ct in enumerate(compute_texts)],
            "\nEVALUATION: ", reasoning.future.text
        ),
        model="Llama3Instruct405B"
    )

    res = substrate.run(answer)
    
    # Check if the output is a diff
    check_diff = ComputeJSON(
        prompt=sb.concat(
            "Analyze the following output and determine if it is a unified diff or a complete file. ",
            "A unified diff should contain lines starting with '+', '-', or ' ' (space) to indicate changes. ",
            "Output a JSON object with 'is_diff' set to true if it's a unified diff, or false if it's a complete file.\n\n",
            "Output to analyze:\n", res.get(answer).text
        ),
        json_schema={
            "type": "object",
            "properties": {
                "is_diff": {
                    "type": "boolean",
                    "description": "True if the output is a unified diff, False if it's a complete file.",
                },
            },
            "required": ["is_diff"]
        },
        model="Llama3Instruct8B"
    )

    diff_result = substrate.run(check_diff)
    
    try:
        result = diff_result.get(check_diff)
        logging.info(f"Diff check response: {result}")
        
        if hasattr(result, 'json_object') and isinstance(result.json_object, dict):
            is_diff = result.json_object.get('is_diff', False)
            if isinstance(is_diff, str):
                is_diff = is_diff.lower() == 'true'
            logging.info(f"Interpreted is_diff value: {is_diff}")
        else:
            logging.error("Response does not contain expected 'json_object' attribute")
            raise AttributeError("Missing or invalid 'json_object' attribute")
    except AttributeError as e:
        logging.error(f"Failed to get a valid response from diff check: {str(e)}")
        sys.exit(1)

    if not is_diff:
        if is_retry:
            logging.error("Failed to generate a valid diff after retry. Exiting.")
            sys.exit(1)
        logging.warning("The output is not a unified diff. Retrying diff generation.")
        return run_comparison(is_retry=True, compute_texts=compute_texts, reasoning=reasoning, prompt=prompt, file_content=file_content, selected_file=selected_file)

    logging.info("Run completed successfully.")
    
    # New ComputeText for generating the entire updated file
    full_file_output = ComputeText(
        prompt=sb.concat(
            "Given the original file content and the finalized diff, output the entire updated file content. ",
            "Do not omit any parts of the file. Wrap the entire output in python``` code blocks. ",
            "Here's the original file content:\n\n", file_content,
            "\n\nAnd here's the finalized diff:\n\n", res.get(answer).text,
            "\n\nNow, please provide the entire updated file content:"
        ),
        model="Llama3Instruct405B"
    )
    
    full_file_result = substrate.run(full_file_output)
    
    print("Final Answer (Full Updated File):")
    print(full_file_result.get(full_file_output).text)
    
    # Get the updated content
    updated_content = full_file_result.get(full_file_output).text

    # Find the start and end of the code block
    start_marker = "```python"
    end_marker = "```"
    start_index = updated_content.find(start_marker)
    end_index = updated_content.rfind(end_marker)

    if start_index != -1 and end_index != -1:
        # Extract the code between the markers
        code_content = updated_content[start_index + len(start_marker):end_index].strip()
    else:
        # If markers are not found, use the entire content
        logging.warning("Could not find expected code block markers. Using full output.")
        code_content = updated_content.strip()

    # Write the changes back to the file
    if write_file_content(selected_file, code_content):
        print(f"Changes have been written to {selected_file}")
    else:
        print(f"Failed to write changes to {selected_file}")

if __name__ == "__main__":
    run_comparison()