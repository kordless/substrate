import os
import json
import importlib.util
import logging
from substrate import Substrate, RunPython, sb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_DIR = os.path.expanduser('~/.config/substrate/')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
FUNCTIONS_DIR = 'functions'

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        api_key = input("Please enter your Substrate API key: ")
        config = {'api_key': api_key}
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print(f"Config file created at {CONFIG_FILE}")
        return config

config = load_or_create_config()
api_key = config['api_key']

substrate = Substrate(api_key=api_key)

def load_functions_from_directory(directory):
    functions = {}
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            module_name = filename[:-3]  # Remove .py extension
            file_path = os.path.join(directory, filename)
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Read the file content to extract pip_install_strings
            with open(file_path, 'r') as f:
                file_content = f.read()
                pip_install_line = next((line for line in file_content.split('\n') if line.startswith('pip_install_strings =')), None)
                if pip_install_line:
                    pip_install_strings = eval(pip_install_line.split('=')[1].strip())
                else:
                    pip_install_strings = []
            
            # Get all functions from the module that are decorated with @substrate_function
            for item_name in dir(module):
                item = getattr(module, item_name)
                if callable(item) and hasattr(item, 'is_substrate_function'):
                    functions[f"{module_name}.{item_name}"] = {
                        'function': item,
                        'pip_install_strings': pip_install_strings
                    }
    
    return functions

# Load all functions from the 'functions' directory
available_functions = load_functions_from_directory(FUNCTIONS_DIR)
print(available_functions)

# Get the function references for the chain
take_screenshot_function = available_functions['browser.take_screenshot']['function']

# Set up the chain of operations, but don't execute it yet
screenshot = RunPython(
    function=take_screenshot_function,
    kwargs={
        'url': 'https://news.ycombinator.com/news'
    },
    pip_install=available_functions['browser.take_screenshot']['pip_install_strings'],
)

# Run the entire chain by executing the last node
"""
format_res = substrate.run(screenshot)
print(dir(format_res))
format_out = format_res.get(screenshot)
print(dir(format_out))
print(format_out.json)
"""

# Get the function references for the chain
process_image_with_easyocr = available_functions['ocr.process_image_with_easyocr']['function']

# Prepare the second function (fb.format) but don't run it yet
ocr = RunPython(
    function=process_image_with_easyocr,
    kwargs={
        'screenshot_base64': sb.format("{screenshot}", screenshot=screenshot.future.output['screenshot_base64'])
    },
    pip_install=available_functions['ocr.process_image_with_easyocr']['pip_install_strings'],
)

# Run the entire chain by executing the last node
format_res = substrate.run(ocr)
print(dir(format_res))
print(format_res.json)
print(format_res.request_id)
format_out = format_res.get(ocr)
print(format_out.output)
