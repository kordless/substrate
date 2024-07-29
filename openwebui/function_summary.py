# Function Summary

# File: .\proxy.py
def file_summary():
    imports = ['os', 'json', 'logging', 'datetime.datetime', 'quart.Quart', 'quart.request', 'quart.jsonify', 'quart.Response', 'substrate.Substrate', 'substrate.Llama3Instruct70B']
    decorators = []
    functions = ['load_or_create_config']
    function_calls = ['logging.basicConfig', 'Quart', 'os.path.expanduser', 'os.path.join', 'os.path.exists', 'open', 'json.load', 'logging.info', 'input', 'os.makedirs', 'open', 'json.dump', 'logging.info', 'logging.error', 'str', 'load_or_create_config', 'logging.error', 'exit', 'config.get', 'logging.error', 'exit', 'Substrate', 'headers.get', 'logging.debug', 'logging.debug', 'logging.debug', 'logging.debug', 'json.loads', 'jsonify', 'request.get_json', 'logging.debug', 'jsonify', 'None.replace', 'data.get', 'data.get', 'data.get', 'data.get', 'data.get', 'jsonify', 'jsonify', 'None.join', 'None.capitalize', 'Llama3Instruct70B', 'Llama3Instruct70B', 'Llama3Instruct70B', 'Llama3Instruct70B', 'datetime.utcnow', 'substrate.async_stream', 'response.async_iter', 'None.isoformat', 'datetime.utcnow', 'json.dumps', 'datetime.utcnow', 'None.total_seconds', 'json.dumps', 'end_time.isoformat', 'int', 'Response', 'sse_stream', 'sse_stream', 'result.append', 'json.loads', 'jsonify', 'logging.error', 'str', 'jsonify', 'app.route', 'None.isoformat', 'datetime.utcnow', 'valid_models.items', 'jsonify', 'logging.error', 'str', 'jsonify', 'app.route', 'jsonify', 'logging.error', 'str', 'jsonify', 'app.route', 'app.run']
    return {
        'imports': imports,
        'decorators': decorators,
        'functions': functions,
        'function_calls': function_calls
    }

