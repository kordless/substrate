# Function Summary

# File: inception/main.py
def file_summary():
    imports = ['os', 'sys', 'json', 'importlib.util', 'inspect', 'substrate.Substrate', 'substrate.ComputeJSON', 'substrate.RunPython']
    decorators = []
    functions = ['load_or_create_config', 'load_functions_from_directory']
    function_calls = ['os.path.expanduser', 'os.path.join', 'os.path.exists', 'open', 'json.load', 'input', 'os.makedirs', 'open', 'json.dump', 'print', 'load_or_create_config', 'Substrate', 'os.listdir', 'filename.endswith', 'os.path.join', 'importlib.util.spec_from_file_location', 'importlib.util.module_from_spec', 'spec.loader.exec_module', 'open', 'f.read', 'next', 'file_content.split', 'line.startswith', 'eval', 'None.strip', 'pip_install_line.split', 'dir', 'getattr', 'callable', 'hasattr', 'None.lower', 'input', 'input', 'ComputeJSON', 'substrate.run', 'response.json.get', 'next', 'iter', 'print', 'print', 'print', 'print', 'print', 'os.makedirs', 'os.path.join', 'open', 'f.write', 'f.write', 'args.split', 'f.write', 'line.strip', 'f.write', 'pip_install_strings.split', 'f.write', 'line.strip', 'f.write', 'f.write', 'f.write', 'f.write', 'f.write', 'f.write', 'code.split', 'enumerate', 'None.startswith', 'line.strip', 'code_lines.insert', 'f.write', 'None.join', 'open', 'f.read', 'compile', 'print', 'print', 'print', 'os.remove', 'print', 'sys.exit', 'load_functions_from_directory', 'print', 'list', 'available_functions.keys', 'enumerate', 'print', 'int', 'input', 'len', 'print', 'print', 'print', 'inspect.signature', 'params.items', 'input', 'input', 'eval', 'RunPython', 'substrate.run', 'res.get', 'print', 'print']
    return {
        'imports': imports,
        'decorators': decorators,
        'functions': functions,
        'function_calls': function_calls
    }

