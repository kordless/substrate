# Function registry to define the stubs
function_registry = {
    "check_weather": {
        "params": {"location": "str", "date": "str"},
        "output_type": "dict"
    },
    "crawl_url": {
        "params": {"url": "str"},
        "output_type": "str"
    }
}

# Generalized function that will return the function signature instead of executing it
def generalized_function(func_name: str, params: dict):
    if func_name not in function_registry:
        return f"Function '{func_name}' is not registered."

    expected_params = function_registry[func_name]["params"]

    # Check if the provided params match the expected params
    if set(params.keys()) != set(expected_params.keys()):
        return f"Parameter mismatch. Expected parameters: {expected_params}, provided: {list(params.keys())}"
    
    # Return the function signature
    return {
        "function_name": func_name,
        "params": expected_params,
        "output_type": function_registry[func_name]["output_type"]
    }

# Example usage - these are stubs and do not perform the actual functions
def check_weather(location: str, date: str):
    return generalized_function("check_weather", {"location": location, "date": date})

def crawl_url(url: str):
    return generalized_function("crawl_url", {"url": url})

# Testing the stubs
print(check_weather("New York", "2024-08-05"))
print(crawl_url("https://example.com"))
