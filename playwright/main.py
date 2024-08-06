import os
import sys
import json
import importlib.util
import inspect
from substrate import Substrate, RunPython

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

# Print available functions with numbers
print("Available functions:")
function_names = list(available_functions.keys())
for index, func_name in enumerate(function_names, start=1):
    print(f"{index}. {func_name}")

# Ask user to enter a number
while True:
    try:
        selection = int(input("Enter the number of the function you want to run: "))
        if 1 <= selection <= len(function_names):
            function_to_run = function_names[selection - 1]
            break
        else:
            print("Invalid selection. Please enter a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")

print(f"You selected: {function_to_run}")

# To actually run the function:
if function_to_run in available_functions:
    function_info = available_functions[function_to_run]
    function = function_info['function']
    pip_install_strings = function_info['pip_install_strings']
    
    # Get the function's parameters
    params = inspect.signature(function).parameters
    
    # Prompt for each parameter
    kwargs = {}
    for param_name, param in params.items():
        # Check if the parameter has a default value
        if param.default is param.empty:
            # No default value, we need to prompt
            value = input(f"Enter value for '{param_name}': ")
        else:
            # There's a default value, make it optional
            value = input(f"Enter value for '{param_name}' (default: {param.default}): ")
            if not value:  # If user doesn't input anything, use the default
                value = param.default
        
        # Try to evaluate the input as a Python expression
        try:
            kwargs[param_name] = eval(value)
        except:
            # If eval fails, just use the string value
            kwargs[param_name] = value

    # Create the RunPython object with the selected function
    md = RunPython(
        function=function,
        kwargs=kwargs,
        pip_install=pip_install_strings,
    )

    # Run the function
    res = substrate.run(md)
    out = res.get(md)
    print(dir(out))
    print(out.stdout)
    print(out.stderr)
    print(out.output)  # (output of the selected function)
else:
    print(f"Function '{function_to_run}' not found.")