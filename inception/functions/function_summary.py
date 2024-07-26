# Function Summary

# File: inception/functions/markdown.py
def file_summary():
    imports = ['requests', 'bs4.BeautifulSoup', 'markdownify.markdownify']
    decorators = ['substrate_function']
    functions = ['substrate_function', 'markdown']
    function_calls = ['requests.get', 'BeautifulSoup', 'md', 'str']
    return {
        'imports': imports,
        'decorators': decorators,
        'functions': functions,
        'function_calls': function_calls
    }

